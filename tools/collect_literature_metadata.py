"""Recover literature candidates from public metadata; never publish automatically.

No API key, login, scraping proxy, or paid service is required. A successful
metadata query is NOT proof of complete publisher coverage or a first-online date.
"""
import argparse
import datetime as dt
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from literature_delivery import unseen_candidates


def clean(value):
    return html.unescape(re.sub(r"<[^>]+>", "", str(value or ""))).strip()


def key(value):
    return re.sub(r"[^a-z0-9]", "", clean(value).casefold())


def date_value(field):
    parts = (field or {}).get("date-parts", [[]])[0]
    # Do not invent a day for month-only or year-only metadata.
    return "-".join(map(lambda n: str(n).zfill(2), parts)) if parts else None


def full_given_name(value):
    return bool(value) and not re.fullmatch(r"[A-Z](?:[.\s-]*[A-Z])*\.?", value.strip())


class Client:
    def __init__(self, timeout=20, attempts=3):
        self.timeout, self.attempts = timeout, attempts

    def get(self, base, params):
        url = base + "?" + urllib.parse.urlencode(params)
        for attempt in range(self.attempts):
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "HMD-Lab-Literature/1.0 (public scholarly metadata)",
                    "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    raw = response.read()
                # HTML challenge/Unavailable pages and malformed JSON are failures,
                # including when a server returns HTTP 200.
                return json.loads(raw), url
            except urllib.error.HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt + 1 == self.attempts:
                    raise
                delay = exc.headers.get("Retry-After", "")
                # Never hammer a rate-limited source or block for minutes.
                if delay.isdigit() and int(delay) > 45:
                    raise RuntimeError("Rate limited; Retry-After exceeds this run's wait budget") from exc
                time.sleep(max(int(delay) if delay.isdigit() else 0, 2 ** (attempt + 1)))
            except (TimeoutError, OSError):
                if attempt + 1 == self.attempts:
                    raise
                time.sleep(2 ** (attempt + 1))


def crossref(client, source, first, last, field):
    items, seen, cursor, seen_cursors = [], set(), "*", set()
    total = None
    while True:
        route = "prefixes/" + source["prefix"] if source.get("prefix") else "journals/" + source["issn"]
        data, url = client.get(
            "https://api.crossref.org/" + route + "/works",
            {"filter": f"from-{field}-date:{first},until-{field}-date:{last}",
             "rows": 1000, "cursor": cursor})
        message = data["message"]
        if not isinstance(message.get("items"), list):
            raise ValueError("Crossref response has no items array")
        total = message["total-results"]
        batch = message["items"]
        for item in batch:
            names = item.get("container-title", [])
            if not source.get("prefix") and not any(key(name) == key(source["journal"]) for name in names):
                raise ValueError("ISSN/title mismatch: " + repr(names))
            doi = item.get("DOI", "").lower()
            if not doi:
                raise ValueError("Missing Crossref DOI")
            if doi not in seen:
                seen.add(doi)
                items.append((item, url))
        if len(seen) >= total:
            return items
        next_cursor = message.get("next-cursor")
        if not batch or not next_cursor or next_cursor in seen_cursors:
            raise ValueError(f"Incomplete Crossref pagination: {len(seen)}/{total}")
        seen_cursors.add(next_cursor)
        cursor = next_cursor
        time.sleep(1)


def europepmc(client, source, first, last):
    results, cursor, seen_cursors = [], "*", set()
    while True:
        data, url = client.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", {
            "query": f'ISSN:{source["issn"]} AND FIRST_PDATE:[{first} TO {last}]',
            "format": "json", "resultType": "core", "pageSize": 1000,
            "cursorMark": cursor})
        batch = data["resultList"]["result"]
        results.extend((item, url) for item in batch)
        if len(results) >= data["hitCount"]:
            return results
        following = data.get("nextCursorMark")
        if not batch or not following or following in seen_cursors:
            raise ValueError("Incomplete Europe PMC pagination")
        seen_cursors.add(following)
        cursor = following
        time.sleep(.4)


def from_crossref(item, url, journal):
    authors = [clean(a.get("name") or " ".join(filter(None, [a.get("given"), a.get("family")])))
               for a in item.get("author", [])]
    return {"doi": item["DOI"].lower(), "title": clean((item.get("title") or [""])[0]),
            "journal": journal, "authors": [a for a in authors if a],
            "authorsComplete": bool(authors) and all(authors) and all(
                a.get("name") or full_given_name(a.get("given")) for a in item.get("author", [])),
            "online_date": date_value(item.get("published-online")),
            "posted_date": date_value(item.get("posted")),
            "reported_date": date_value(item.get("published")),
            "url": "https://doi.org/" + item["DOI"].lower(),
            "abstract_for_review": clean(item.get("abstract")),
            "editors": [clean(a.get("name") or " ".join(filter(None, [a.get("given"), a.get("family")])))
                        for a in item.get("editor", [])],
            "sources": [{"service": "Crossref", "url": url}]}


def merge_epmc(records, item, url, journal):
    doi = (item.get("doi") or "").lower()
    identity = doi or "pmid:" + str(item.get("id", ""))
    if not identity or identity == "pmid:":
        raise ValueError("Europe PMC record has no persistent identifier")
    record = records.setdefault(identity, {"doi": doi or None, "title": clean(item.get("title")),
        "journal": journal, "authors": [], "authorsComplete": False, "online_date": None,
        "reported_date": item.get("firstPublicationDate"),
        "url": "https://doi.org/" + doi if doi else "https://europepmc.org/article/MED/" + item["id"],
        "sources": [], "editors": []})
    author_list = item.get("authorList", {}).get("author", [])
    names = [clean(a.get("collectiveName") or " ".join(filter(None, [a.get("firstName"), a.get("lastName")]))
                   or a.get("fullName")) for a in author_list]
    if names and all(names):
        complete = all(a.get("collectiveName") or full_given_name(a.get("firstName")) for a in author_list)
        # Do not replace verified full Crossref names with initials from NLM.
        if complete or not record.get("authorsComplete"):
            record["authors"], record["authorsComplete"] = names, complete
    online = item.get("electronicPublicationDate")
    if online:
        if record.get("online_date") and record["online_date"] != online:
            record["date_conflict"] = [record["online_date"], online]
        else:
            record["online_date"] = online
    record["first_publication_date"] = item.get("firstPublicationDate")
    record["abstract_for_review"] = clean(item.get("abstractText")) or record.get("abstract_for_review", "")
    record["sources"].append({"service": "Europe PMC", "url": url})


def eligibility(record, first, last):
    online = record.get("online_date") or record.get("posted_date")
    if record.get("date_conflict"):
        return "date_conflict_review_required"
    if not online or len(online) != 10:
        return "first_online_date_unverified"
    if online in (first, last):
        return "cutoff_day_time_unverified"
    return "in_window_day_verified" if first < online < last else "outside_window"


def weekly_read_counts(records, journal, first, last):
    """Count metadata inspected for this edition, including undated records.

    Cutoff days remain uncertain without time-of-day evidence. Records from an
    unverified Research Square portfolio are never attributed to that portfolio.
    """
    if journal == "Research Square - Nature Portfolio":
        return {"readCount": None, "readCountIsLowerBound": False,
                "readCountBasis": "Nature Portfolio membership not verified"}
    examined, pending = set(), set()
    for record in records:
        if record.get("journal") != journal:
            continue
        identity = record.get("doi") or record.get("url")
        if not identity:
            continue
        examined.add(identity)
        date = (record.get("online_date") or record.get("first_publication_date")
                or record.get("posted_date") or record.get("reported_date"))
        if not date or len(date) != 10 or date in (first, last) or record.get("date_conflict"):
            pending.add(identity)
    return {"readCount": len(examined), "readCountIsLowerBound": False,
            "readCountDatePending": len(pending),
            "readCountBasis": "Unique metadata inspected in this run, including baseline/backfill; not a publication total"}


def collect(client, source, first, last, lookback=21):
    records, attempts = {}, []
    discovery_start = (dt.date.fromisoformat(first) - dt.timedelta(days=lookback)).isoformat()
    queries = [("posted", discovery_start)] if source.get("prefix") else [
        ("online-pub", discovery_start), ("pub", discovery_start), ("created", discovery_start)]
    for field, start in queries:
        try:
            items = crossref(client, source, start, last, field)
            for item, url in items:
                record = from_crossref(item, url, source["journal"])
                identity = record["doi"]
                if identity in records:
                    records[identity]["sources"].extend(record["sources"])
                else:
                    records[identity] = record
            attempts.append({"service": "Crossref", "query": field,
                             "status": "ok", "records": len(items), "pagination_exhausted": True})
        except Exception as exc:
            attempts.append({"service": "Crossref", "query": field, "status": "error", "detail": str(exc)})
        time.sleep(1)
    if not source.get("prefix"):
        try:
            items = europepmc(client, source, discovery_start, last)
            for item, url in items:
                merge_epmc(records, item, url, source["journal"])
            attempts.append({"service": "Europe PMC", "status": "ok", "records": len(items),
                             "pagination_exhausted": True})
        except Exception as exc:
            attempts.append({"service": "Europe PMC", "status": "error", "detail": str(exc)})
    for record in records.values():
        if source.get("prefix"):
            record["preprint"] = True
            record["portfolio_membership"] = "unverified; prefix is not a Nature Portfolio filter"
        record["date_status"] = eligibility(record, first, last)
        record["eligibility"] = record["date_status"]  # Compatibility: date evidence, NOT a delivery gate.
        record["date_blocks_delivery"] = False
        record["discovery_checked_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        record["editor_check"] = ("metadata_available_requires_official_confirmation"
                                  if record["editors"] else "not_available_in_metadata")
    health = {"journal": source["journal"], "issn": source.get("issn"),
              "status": "partial" if records else "unavailable",
              "access": "metadata_recovered" if records else "no_records_recovered",
              "records_recovered": len(records),
              "in_window_day_verified": sum(r["eligibility"] == "in_window_day_verified" for r in records.values()),
              "attempts": attempts,
              "detail": "Metadata discovery only; publisher completeness, first-online dates, editor credits and indexing delays still require review."}
    health.update(weekly_read_counts(list(records.values()), source["journal"], first, last))
    # A zero-result indexed query never proves the journal published no new work.
    return list(records.values()), health


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="Beijing cutoff day, YYYY-MM-DD")
    parser.add_argument("--end", required=True)
    parser.add_argument("--sources", type=Path, default=Path(__file__).resolve().parents[1]/"data/literature-sources.json")
    parser.add_argument("--journal", action="append", help="Repeat to select named journals")
    parser.add_argument("--output", type=Path, required=True, help="Private/intermediate candidate file, never publish raw abstracts")
    parser.add_argument("--health-output", type=Path, required=True)
    parser.add_argument("--lookback", type=int, default=21)
    parser.add_argument("--delivered-ledger", type=Path,
                        default=Path(__file__).resolve().parents[1]/"data/literature/delivered.json")
    args = parser.parse_args()
    if dt.date.fromisoformat(args.start) >= dt.date.fromisoformat(args.end):
        parser.error("end must follow start")
    sources = json.loads(args.sources.read_text())["journals"]
    ledger = json.loads(args.delivered_ledger.read_text()) if args.delivered_ledger.exists() else {"entries": []}
    if args.journal:
        unknown = set(args.journal) - {s["journal"] for s in sources}
        if unknown:
            parser.error("Unregistered journal: " + ", ".join(sorted(unknown)))
        sources = [s for s in sources if s["journal"] in args.journal]
    output, health = {"start": args.start, "end": args.end, "candidates": []}, {
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "window": {"start": args.start + " 03:30", "end": args.end + " 03:30", "timezone": "Asia/Shanghai"},
        "sources": []}
    for source in sources:
        candidates, status = collect(Client(), source, args.start, args.end, args.lookback)
        output["candidates"].extend(candidates)
        output["unseen_candidate_ids"] = [r.get("doi") or r.get("id") or r.get("url")
                                          for r in unseen_candidates(output["candidates"], ledger)]
        output["delivery_ledger_history_scope"] = ledger.get("history_scope", "No delivered ledger available")
        health["sources"].append(status)
        # Checkpoint after every source so a later failure cannot erase progress.
        for path, value in [(args.output, output), (args.health_output, health)]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        print(source["journal"], status["access"], status["records_recovered"],
              "candidates;", status["in_window_day_verified"], "with in-window online dates", flush=True)


if __name__ == "__main__":
    main()
