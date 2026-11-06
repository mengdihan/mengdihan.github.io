# Repository instructions for Codex

## Publications and citations: mandatory synchronization

Whenever a change adds, removes, reorders, or edits a publication anywhere on the HMD Lab website, treat publication metadata, citation data, and member-selected publications as one coordinated update. This applies to edits made through Codex, including changes to generated pages or their source data.

1. Inspect the publication source data and `tools/build_site.py` before editing. Update the canonical publication entries, and ensure Publications Full List and year-specific pages reflect the same title, authors, venue, year, DOI, and links. Do not manually patch generated HTML in place of source data.
2. Check the Google Scholar profile https://scholar.google.com/citations?user=rjC8MUQAAAAJ&hl=en for current per-paper citation counts and corresponding "Cited by" URLs. Match by DOI where possible; otherwise carefully verify title, authors, and year. Update the canonical `data/scholar-citations.json` records, including provenance/check dates, only for values actually verified. Never invent counts, infer missing counts as zero, or mark an incomplete scrape as fully synchronized.
3. Inspect both Group Current Members and Group Alumni selected-publication data. Add or remove affected selected publications as appropriate to their actual author/member associations; do not assume every new publication belongs in every member's selected list. Ensure citation badges and "Cited by" links for selected papers use the same canonical citation records as Publications.
4. Preserve existing verified citation values if Google Scholar is inaccessible, blocked, or incompletely paginated. Report which publications or counts could not be verified; do not claim a fresh citation sync or change the global checked date unless the intended scope was fully checked.
5. Run the repository's build and verification procedures (normally `python tools/build_site.py` and `python tools/verify_site.py`, plus any applicable checks). Verify consistency across Publications Full List, year pages, Group Current, and Group Alumni, including titles, DOI mappings, citation counts, and outbound Scholar links. After publishing, check the deployment status and report any failure.

This is an **on-publication-change requirement**, not a request to schedule periodic citation scraping. Do not silently omit citation/member checks when updating the publication list. If source access or verification fails, leave old values intact and state the limitation in the change summary.
