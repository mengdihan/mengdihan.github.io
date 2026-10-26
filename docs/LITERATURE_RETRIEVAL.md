# Literature retrieval and recovery

## Verified failure modes

On 2026-10-23 the Science ToC and RSS returned HTTP 403. Cell and ScienceDirect routes returned HTTP 200 with a 195-byte “Site Unavailable” page. IEEE responses varied between a page response and HTTP 418. These are access failures, not evidence of an empty weekly issue. Crossref and Europe PMC public APIs returned usable journal metadata without API keys or a subscription. Some Crossref requests returned 429; honor Retry-After and back off. Do not bypass authentication, CAPTCHAs, rate limits or publisher access controls.

Some deposits have only a month-level issue date and no published-online field. An online-date-only query therefore misses new records. A DOI registration/created date can discover such records but cannot establish when the article was published. Search-engine crawl dates, DOI suffix years, acceptance dates and future print issue dates are not substitutes for the first-online date.

## Workflow

1. Read the latest Journal list in Drive without editing it. Reconcile names and links with `data/literature-sources.json`. This registry covers affected journals; it does not replace the authoritative journal list or imply the other journals should be skipped. Verify any added ISSN against an official journal source. The collector rejects returned Crossref container titles that do not match the configured journal. Fix Nature Protocols to its own official source, never the accidental Nature Photonics link.
2. Try the publisher's current issue AND online-first/archive or dated article list. Validate the content, not just the status code: an “Unavailable”, sign-in, challenge or empty JavaScript shell does not count as a catalogue. Save the checked URL, time, status and limitation. Use supported web retrieval for official HTML/PDF when direct retrieval fails; do not treat search results as an exhaustive issue.
3. Use the collector as a second route. It queries Crossref by online publication, general publication and recent registration with a 21-day discovery lookback; it also queries Europe PMC by journal ISSN and FIRST_PDATE. Cursor pagination must be exhausted; incomplete pagination is reported as a failure. Crossref/Europe PMC indexing can lag. A future run must recheck the lookback and compare its candidates with the published DOI ledger, so late-indexed papers are not silently lost. Classify confirmed older omissions as a dated delayed supplement, not as newly published this week.
4. Review candidates. Only a day-resolved first-online/posted date inside the reporting window qualifies on date alone; either cutoff day still needs time verification for the 03:30 Asia/Shanghai half-open window. Unknown/month-only dates and conflicting dates stay pending. `reported_date`, Crossref created/issued dates and Europe PMC dateOfCreation are discovery/context only. Europe PMC electronicPublicationDate and publisher HTML/PDF can verify an online date. Check whether an earlier online-first version exists before treating a print appearance as new.
5. Author metadata is preserved in full order, including collective authors. The collector does not expand initials. Prefer full given names from Crossref or the structured Europe PMC author list, and verify gaps against the publisher. Never replace complete names with initials. Abstracts in the intermediate file are for editorial review only: write original concise summaries, do not publish raw abstracts. Apply the existing relevance policy; do not silently replace the complete report with a keyword Top 10.
6. Science editor credits: Crossref/NLM metadata often lacks handling editors. Check official article HTML or PDF, including the editorial summary where available. Missing editor metadata does not mean the editor was not Marc Lavine. If credits remain inaccessible, report that this special inclusion rule could not be fully verified; do not claim every Marc Lavine article was found. Keep editor names off the public article cards and chat recommendations, as requested.
7. Research Square has a usable Crossref prefix endpoint. Use posted-date filters and cursor pagination, deduplicate DOI/version relations, and mark all candidates as preprints, not peer reviewed. Prefix 10.21203 covers Research Square generally, NOT just Nature Portfolio. Its broad recovery candidates need independent Nature Portfolio submission/category evidence before claiming that filter. Never infer acceptance, peer review or portfolio membership from the platform name.
8. Update the public edition only after relevance/content/date review and DOI deduplication. Recovered metadata can change a source from unavailable to partial, but does not justify complete. The health report distinguishes records recovered from date-verified candidates. Zero recovered records remains unverified coverage, not “no new papers”. Keep original coverage qualifications until actually resolved.

## Commands

Run from the repository root, with the scheduled cutoff days:

```bash
python tools/collect_literature_metadata.py --start 2026-10-16 --end 2026-10-23 --output /tmp/literature-candidates.json --health-output /tmp/literature-health.json
python tools/test_literature_metadata.py
```

Repeat `--journal 'Device'` to select sources. Dates above are examples, not a fixed run window. Output candidates are intermediate files that may contain full abstracts; keep them out of the public repository and website. A reviewed source-health report with counts, public source URLs and limitations may be committed. Do not publish private interest feedback or unpublished comparisons.

## Public API references

- Crossref REST filters: https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/
- Crossref pagination and date queries: https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/
- Europe PMC REST API: https://europepmc.org/RestfulWebService
- PubMed date fields and API limits: https://www.ncbi.nlm.nih.gov/books/NBK25499/

This is a public-metadata fallback, not a subscription full-text downloader. No new paid service, user login or private report API is needed.

## Reading-count audit and source overrides — 2026-10-23

The registry now covers the monitored journal sources plus Research Square; arXiv and bioRxiv use their own public APIs. Small is excluded by owner instruction, even if still present in the read-only Drive sheet. The journal selector shows reads and selected entries separately. Use `weekly_read_counts` on deduplicated recovery candidates. Count only retrieved records with a day-resolved publication field in the edition window; retain online/first-publication versus reported issue-date evidence and do not turn a count into permission to publish an unverified first-online date. Day-only cutoff records and month-only records remain pending. Existing verified selected entries establish a lower bound, not a complete survey. Preserve per-source read-count evidence and update counters every run.

arXiv API queries use the precise converted UTC cutoff and verify every entry's published timestamp. bioRxiv's `details/biorxiv/START/END/CURSOR/json?category=bioengineering` endpoint was tested with category verification and pagination (30 records per page in this response). Filter version 1 and deduplicate DOI; exclude uncertain cutoff-day records or retain an explicit lower bound. Category totals include updated versions, so do not treat `total` as a new-paper count. Nature Protocols is 1750-2799 online (1754-2189 print); its monitored official path is `/nprot/`, not `/nphoton/`.

The Research Square Nature Portfolio filtered URL returned HTTP 403 on 2026-10-23; the connected-browser attempt timed out. Platform Crossref records remain usable for discovery, but the filtered count is unverified and must be shown as —. Do not claim the filtered browse page was read successfully.

## Latest policy: first-seen baseline and delivery deduplication — 2026-10-23

This owner instruction overrides all older date-based exclusion rules above. Relevant articles with unknown, month-only, conflicting or cutoff-uncertain publication dates may be included after identity, content and source-scope review. Do not hold an otherwise eligible article solely because its exact first-online date is unavailable. Initialize the baseline with newly reviewed eligible candidates now; do not silently discard them as old or mark them delivered before actual delivery.

After baseline setup, select articles not previously delivered, rather than requiring proof of publication within seven days. A weekly edition describes articles newly delivered since the previous run; it is not a guarantee that every article was first published that week. Metadata indexing delays or a recovered source can reveal older unpushed papers. Preserve known publication dates and mark unknown ones as `Publication date unverified`, with nullable `date` and optional truthful `dateLabel`. Keep `first_seen_at`, edition period and publication date distinct; never fabricate a publication date from discovery or DOI registration. Known older omissions may be included as newly discovered/backfill without mislabelling them newly published.

`data/literature/delivered.json` was seeded from the 46 entries in the confirmed published public edition. `tools/literature_delivery.py` normalizes DOI URLs, titles and arXiv/Research Square/bioRxiv version identifiers and returns unseen candidates without a date gate. Add independently verified preprint/formal-version aliases when their identity is established. Do not equate distinct studies from the same group. Candidate screening and rejected/irrelevant entries are not the delivered ledger. Merge accessible historical private/chat delivery IDs privately before claiming comprehensive historical deduplication; the public seed alone does not cover all former Chinese reports.

Only record a new entry as delivered after the message was actually delivered or the website deployment was confirmed successful. A fetch, candidate review or failed deployment must not mark it delivered. Retain delivery edition and confirmation time. First-seen timestamps are editorial bookkeeping, not publication evidence. Baseline review does not require reading an entire journal's historical archive; process the accessible recent/latest candidates, including the currently pending undated records. Revisit incomplete source baselines on later runs.

Read counts in future editions count unique metadata actually inspected for that edition, including undated baseline candidates; they are not publication totals. Distinguish examined candidates, selected entries and actually delivered entries. Historical date-limited counters may remain labelled as lower bounds. Preserve all previous topical preferences, level 1/2 all-content rules for the full report, Marc Lavine inclusion rule without displaying his name, Small exclusion and Research Square Nature Portfolio scope checks. This policy relaxes date accuracy, not content verification, source membership or relevance.


## Research Square Nature Portfolio browser recovery — 23 October 2026

The user-specified path was verified successfully: open https://www.researchsquare.com/browse, select **Nature Portfolio** in **Journals & Platforms**, then press **Search**. The URL remains `/browse`; do not infer filter state from a guessed query-string URL. Confirm the visible selected option and the Nature Portfolio logo on result cards. Historical direct-request HTTP 403 and browser timeouts do not establish that this filtered UI is unreadable.

Ten pages / 100 latest records were inspected (posted 14–22 October), from a filtered catalogue of 5,814 records. The catalogue total is not the current-week publication count. Six relevant preprints were checked on their detail pages for content, authors and posted date and added to the edition (52 total articles). The public audit file stores only observed public list metadata, not full abstracts, account information or browser state. Coverage remains partial because the historical catalogue was not exhaustively scanned.

For future runs use the visible filter, paginate against delivered identities and extend the lookback after interruptions. Check full authors and abstract on detail pages; the Nature Portfolio filter does not mean acceptance by a Nature journal. Label all entries as preprints not peer reviewed. Use DOI/title/version deduplication and mark delivered only after successful publication. If the required browser is unavailable in a future execution, report the execution gap rather than claiming a successful scan or substituting platform-wide counts. Source read counts include actual inspected baseline/backfill records.
