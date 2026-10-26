"""Offline checks for the failure modes that can silently drop new articles."""
import unittest
from collect_literature_metadata import crossref, date_value, eligibility, from_crossref, merge_epmc, weekly_read_counts


class FakeClient:
    def __init__(self, pages):
        self.pages = iter(pages)
    def get(self, base, params):
        return next(self.pages), base


def page(items, total, cursor=None):
    return {"message": {"items": items, "total-results": total, "next-cursor": cursor}}


def paper(doi="10.test/a", journal="Device"):
    return {"DOI": doi, "container-title": [journal], "title": ["A paper"],
            "published": {"date-parts": [[2026, 10]]},
            "author": [{"given": "Mengdi", "family": "Han"}]}


class MetadataTests(unittest.TestCase):
    def test_read_count_includes_undated_baseline_records_and_deduplicates(self):
        records = [{"doi": "10.test/a", "journal": "Device", "online_date": "2026-10-20"},
                   {"doi": "10.test/a", "journal": "Device", "online_date": "2026-10-20"},
                   {"doi": "10.test/b", "journal": "Device", "online_date": "2026-10-23"},
                   {"doi": "10.test/c", "journal": "Device", "reported_date": "2026-10"}]
        count = weekly_read_counts(records, "Device", "2026-10-16", "2026-10-23")
        self.assertEqual(count["readCount"], 3)
        self.assertEqual(count["readCountDatePending"], 2)

    def test_platform_count_is_not_a_portfolio_count(self):
        self.assertIsNone(weekly_read_counts([], "Research Square - Nature Portfolio",
                                            "2026-10-16", "2026-10-23")["readCount"])

    def test_month_only_is_not_made_into_a_day(self):
        record = from_crossref(paper(), "https://api.crossref.org/", "Device")
        self.assertEqual(record["reported_date"], "2026-10")
        self.assertEqual(eligibility(record, "2026-10-16", "2026-10-23"), "first_online_date_unverified")

    def test_created_is_not_a_publication_date(self):
        item = paper()
        item["created"] = {"date-parts": [[2026, 10, 20]]}
        record = from_crossref(item, "https://api.crossref.org/", "Device")
        self.assertIsNone(record["online_date"])

    def test_first_last_days_need_cutoff_time(self):
        for day in ["2026-10-16", "2026-10-23"]:
            self.assertEqual(eligibility({"online_date": day}, "2026-10-16", "2026-10-23"),
                             "cutoff_day_time_unverified")
        self.assertEqual(eligibility({"online_date": "2026-10-20"}, "2026-10-16", "2026-10-23"),
                         "in_window_day_verified")

    def test_complete_pagination_and_dedup(self):
        client = FakeClient([page([paper()], 2, "next"), page([paper("10.test/b")], 2)])
        results = crossref(client, {"journal": "Device", "issn": "2666-9986"},
                           "2026-10-16", "2026-10-23", "pub")
        self.assertEqual(len(results), 2)

    def test_truncated_pages_are_not_complete(self):
        client = FakeClient([page([paper()], 2)])
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            crossref(client, {"journal": "Device", "issn": "2666-9986"},
                     "2026-10-16", "2026-10-23", "pub")

    def test_wrong_issn_cannot_silently_mix_journals(self):
        with self.assertRaisesRegex(ValueError, "ISSN/title mismatch"):
            crossref(FakeClient([page([paper(journal="Cell")], 1)]),
                     {"journal": "Device", "issn": "2666-9986"},
                     "2026-10-16", "2026-10-23", "pub")

    def test_date_conflicts_require_review(self):
        record = from_crossref(paper(), "https://api.crossref.org/", "Device")
        record["online_date"] = "2026-10-18"
        records = {record["doi"]: record}
        merge_epmc(records, {"doi": record["doi"], "electronicPublicationDate": "2026-10-19"},
                   "https://europepmc.org", "Device")
        self.assertEqual(eligibility(record, "2026-10-16", "2026-10-23"), "date_conflict_review_required")

    def test_initials_do_not_replace_complete_names(self):
        record = from_crossref(paper(), "https://api.crossref.org/", "Device")
        records = {record["doi"]: record}
        merge_epmc(records, {"doi": record["doi"], "authorList": {"author": [
            {"firstName": "M", "lastName": "Han", "fullName": "Han M"}]}}, "https://europepmc.org", "Device")
        self.assertEqual(record["authors"], ["Mengdi Han"])
        self.assertTrue(record["authorsComplete"])

    def test_posted_date_supports_preprints(self):
        record = {"posted_date": "2026-10-19", "preprint": True}
        self.assertEqual(eligibility(record, "2026-10-16", "2026-10-23"), "in_window_day_verified")


if __name__ == "__main__":
    unittest.main()
