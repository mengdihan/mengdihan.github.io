import unittest
from literature_delivery import identifiers, unseen_candidates, ledger_from_published


class DeliveryTests(unittest.TestCase):
    def test_unknown_date_is_not_a_rejection(self):
        item = {"doi": "10.test/unknown", "title": "Unknown publication date", "date": None}
        self.assertEqual(unseen_candidates([item], {"entries": []}), [item])

    def test_normalized_doi_prevents_repush(self):
        known = {"doi": "https://doi.org/10.1234/ABC"}
        self.assertEqual(unseen_candidates([{"doi": "10.1234/abc"}], {"entries": [known]}), [])

    def test_preprint_versions_are_one_delivery(self):
        known = {"doi": "10.21203/rs.3.rs-12345/v1"}
        self.assertEqual(unseen_candidates([{"doi": "10.21203/rs.3.rs-12345/v2"}], {"entries": [known]}), [])

    def test_title_match_links_preprint_and_journal(self):
        known = {"doi": "10.1101/2026.01.01.123456", "title": "Magnetic sensors: a study"}
        self.assertEqual(unseen_candidates([{"doi": "10.1234/final", "title": "Magnetic sensors—a study"}], {"entries": [known]}), [])

    def test_only_delivered_entries_are_seeded(self):
        edition = {"id": "2026-10-23", "articles": [{"doi": "10.1234/pushed", "title": "Delivered"}]}
        ledger = ledger_from_published([edition], "2026-10-23")
        original = len(ledger["entries"])
        unseen_candidates([{"doi": "10.1234/candidate", "title": "Candidate"}], ledger)
        self.assertEqual(len(ledger["entries"]), original)
        self.assertEqual(ledger["entries"][0]["first_delivered_edition"], "2026-10-23")


if __name__ == "__main__":
    unittest.main()
