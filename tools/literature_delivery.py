"""Delivery-based deduplication. Discovery dates do not gate publication.

The ledger contains successfully delivered entries only. Never populate it from
an unreviewed candidate file, a failed deployment, or a list of rejected papers.
"""
import json
import re
import unicodedata
from urllib.parse import unquote


def identifiers(record):
    values = set()
    for raw in [record.get("doi"), record.get("id"), record.get("preprint_id"), *record.get("aliases", [])]:
        if not raw:
            continue
        value = unquote(str(raw)).strip().lower()
        doi = re.search(r"10\.\d{4,9}/[^\s?#]+", value)
        if doi:
            value = doi[0].rstrip(".,;")
            if value.startswith(("10.21203/", "10.1101/", "10.64898/")):
                value = re.sub(r"/?v\d+$", "", value)
            values.add("doi:" + value)
        elif "arxiv" in value or re.fullmatch(r"\d{4}\.\d{4,5}(?:v\d+)?", value):
            match = re.search(r"\d{4}\.\d{4,5}(?:v\d+)?", value)
            if match:
                values.add("arxiv:" + re.sub(r"v\d+$", "", match[0]))
        else:
            values.add("id:" + value)
    title = record.get("title")
    if title:
        normalized = "".join(c for c in unicodedata.normalize("NFKC", title).casefold() if c.isalnum())
        if normalized:
            values.add("title:" + normalized)
    return values


def unseen_candidates(records, ledger):
    """Return unpushed candidates for content/scope review, regardless of date.

    This function does not update the ledger or decide research relevance. It
    also deduplicates the current batch, including DOI/title/version aliases.
    """
    seen = {key for record in ledger.get("entries", []) for key in identifiers(record)}
    result = []
    for record in records:
        keys = identifiers(record)
        if not keys:
            raise ValueError("A candidate needs a stable identifier or title")
        if seen.intersection(keys):
            continue
        result.append(record)
        seen.update(keys)
    return result


def ledger_from_published(editions, confirmed_on):
    """Call only with editions independently confirmed delivered/published."""
    entries, seen = [], set()
    for edition in editions:
        for article in edition["articles"]:
            keys = identifiers(article)
            if seen.intersection(keys):
                continue
            if not keys:
                raise ValueError("A published entry has no stable identity")
            seen.update(keys)
            entry = {key: article[key] for key in ("id", "doi", "preprint_id", "title", "aliases") if article.get(key)}
            entry.update(first_delivered_edition=edition["id"], delivery_confirmed_on=confirmed_on)
            entries.append(entry)
    return {"version": 1, "policy": "Only confirmed delivered entries; unknown publication dates are allowed",
            "history_scope": "Confirmed public editions only; merge accessible private/chat delivery history before asserting full historical deduplication",
            "entries": entries}
