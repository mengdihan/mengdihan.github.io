## Direct Google connection — 31 October 2026

The account panel exposes Connect with Google alongside Log in (email). It uses the existing Firebase Google popup flow, hides both actions after authentication, and restores them on sign-out. The Personalized recommendations caption and its hover/focus disclosure have been removed; article content, ranking, and private feedback remain unchanged.

## Read Later and mark filters — 30 October 2026

Read Later is an independent, owner-only bookmark stored as `bioeReadLater: true` in the existing private feedback note JSON; preserve legacy text and any other JSON fields. Existing shared Like/Useful/Not relevant signals and deployed rules are unchanged. Bookmark-only saves write no shared reaction/event. Read Later can coexist with any reaction and does not contribute to community totals. Personal order is both Like and Useful, either positive, Read Later, unmarked, Not relevant; a negative reaction takes precedence over a bookmark.

Four checked-by-default checkboxes in the main filter panel select the reader's Like, Useful, Not relevant and Read Later marks with OR semantics in either sorting view. All four checked means no mark restriction, including unmarked articles; none checked means no results. Reset filters checks all four and restores all other filters. Incoming snapshots and clicks preserve both displayed membership and order: undoing a mark under a mark filter must not remove the article until refresh or an explicit filter/search/sort action. Bookmarks sync through the same UID-isolated feedback listener. Keep the current-feedback tests and private schema; never send bookmark notes to shared documents.

## Current-edition feedback sorting — 30 October 2026

This owner instruction supersedes earlier frozen-edition and per-reader community-average sorting rules. Current reactions take effect on refresh or an explicit search/topic/source/edition/sort/reset action. Save/undo and incoming feedback snapshots update buttons, counts and names immediately but preserve the displayed article order and focus; never automatically reorder after a reaction.

Personal preference: both Like and Useful first; either mark next; unmarked next; Not relevant last. Account-specific feedback is read only for the signed-in UID. Existing bounded content-affinity ranking may break ties within these groups. Community average (retained UI label): sort by current total Like + Useful − Not relevant, not per-user averages; one current mark of each kind per user/article, double positive counts twice, undo removes the mark. Equal community scores fall back to editorial relevance and title. Use current communityReactions, not a publication-cutoff query. Preserve append-only reactionEvents for history and existing atomic writes/security rules. Initial login hydration may establish the order once before reactions are enabled; subsequent data synchronization must not move cards.

Keep publication timestamps immutable as publication metadata; they no longer freeze article-reaction sorting. Do not claim saved article-interest profiles are fully integrated by this change; that separate feature is unchanged. No live user/private data belongs in repository tests.

## Content-based article interests (25 October 2026)

The interest entry now searches Crossref and Europe PMC by title or DOI, shows matching title/journal/year/authors, reads the selected article's available abstract and preferably Europe PMC open full-text XML, and asks the reader to confirm before saving. No readable substantive content means no save; network failures are explicit. Search uses public services without cookies or application credentials. Content terms are extracted from the retrieved text and feed the existing bounded text-similarity recommender; do not claim an LLM has interpreted the full paper. Paywalled/unavailable full text is not claimed as read.

Private schema is unchanged: note holds a bounded v2 JSON profile with action/add, actual abstract/open-full-text basis, source URL, text excerpt and content terms; doi and journal are confirmed metadata. Removal remains an append-only remove event. Only content-backed entries train future Personal editions. Old title-only entries remain visible as unresolved and no longer train recommendations. Preserve the resolver, confirmation UI and edition cutoff; never publish user preferences to GitHub or claim the scheduled task reads them.

## Private title memory and compact disclosures (24 October 2026)

The top account frame has one Log in button; its dialog contains Google, email sign-in and account creation. The caption is centered and reads “Private preferences across devices”. Sources and recommendation help are mutually exclusive. Member publication disclosures are also exclusive within each Current or Alumni page.

Signed-in readers can enter a title above the article list and remove saved titles. Each action appends a new owner-only feedback document using the existing deployed schema: key/id `interest:<random UUID>`, empty doi, title, journal `Personal reading interests`, empty signals, note `add` or `remove`, and a server updatedAt. SHA-256(key) remains the document ID. The dedicated saveInterest method writes only the private document, never a community reaction or shared event. The existing rules require no change. The adapter clears private records on sign-out; no title memory is sent to GitHub or the weekly task.

The client folds title events at the edition cutoff, normalizes titles to prevent duplicates, and uses active titles as positive text-similarity examples in Personal. Removal affects future editions, retaining the historical event needed to reproduce older rankings. New entries cannot reorder the current edition. This is keyword similarity using the existing recommender, with no claim that an AI has read the entered article.

Anonymous visitors can read the complete public article pool. The existing Firestore rules require authentication for live community reaction history; that rule remains unchanged. When no community history is available, ranking falls back to editorial relevance. Do not claim an anonymous browser can retrieve live community averages, expose reader names publicly, or fabricate a public aggregate.

# BioE Radar accounts

## Email and password (24 October 2026)

Email/password is enabled alongside Google in Firebase Authentication. The Email button opens a native dialog with sign-in, account creation and password reset modes. New readers choose a public display name and a password of at least eight characters. The profile name is saved and the Firebase ID token is refreshed before named reactions are written, preserving the existing name-claim validation. Email addresses and passwords are never stored in Firestore, public reaction records, GitHub, or application logs. Firebase manages credentials and reset emails. The reset response is intentionally generic.

The dialog form uses `method="dialog"`: credentials are never sent as a URL query or posted to GitHub Pages. The client prevents the native submit and calls the official Firebase SDK; password inputs are cleared after submission and on close. The existing Google flow, UID-scoped preferences, edition cutoffs, community averaging and sync remain in place. WeChat is deferred; no certification purchase or billing upgrade is needed for this change.

The production adapter passed local Auth emulator registration, name-claim refresh, sign-out/sign-in, wrong-password, duplicate-address, reset and separate-account checks. UI checks cover mode transitions, reset feedback, password clearing, and 1366/390/320px layouts. Run the Auth test with `firebase emulators:exec --only auth --project demo-bioe-email --config bioe-account/email-emulator.json 'node --test bioe-account/test/email-auth.cjs'`, with Firebase SDK dependencies installed. `email-ui.cjs` uses Playwright and the same local preview conventions as `account-ui.cjs`.

## Named reactions and edition versions (24 October 2026)

Buttons are Like, Useful and Not relevant. The existing internal `more` signal now labels Like; legacy records need no migration. Notes remain owner-only. New signal changes atomically update private feedback, a signed-in-readable `communityReactions/{uid}_{articleSHA}` document (verified display name, no notes/email), and an immutable `reactionEvents/{autoID}`. Legacy private feedback is never automatically published. Undo clears the current shared signal; historical events are retained for edition snapshots.

The Personal and Community average views share the article pool. Rankings use only feedback at/before that edition's immutable `publishedAt` timestamp, with its Beijing `end` time as the legacy fallback. Current clicks update controls and names immediately but cannot change that edition's ranking. Future editions consume these signals. Community scores average the latest non-empty pre-cutoff signal from each reader per article. Like weighs 1, Useful 2, Not relevant -1; readers cannot add duplicate votes. Editorial relevance still bounds similarity-based adjustments. The first edition has no earlier community history, so both versions may initially look alike.

The reaction tooltip lists current reader names on hover or keyboard focus. Shared names and community averages require Google sign-in. UI notes have no AI-processing disclaimer. The recommendation disclosure stays in its own full-width row, with its summary anchored right while expanded content flows below.

Rules were tested with the official Firestore emulator: seven suites cover valid atomic saves/undo, anonymous/cross-owner denial, name spoofing, timestamps, standalone writes, field injection, invalid signals, strict bounds and immutable events. Ranking tests additionally cover next-edition cutoffs, equal per-article reader weighting, and undo. Run `NODE_PATH=<Firebase dependencies> node --test bioe-account/test/community-rules.cjs` with the emulator at 127.0.0.1:8080. The rules remain a prototype for review before broad sharing.

Google Authentication and Firestore are configured in Firebase project `bioe-radar` (Spark). The authorized public domain is `hanmd1990.github.io`; the default Standard Firestore database is in `asia-east2` (Hong Kong). No billing upgrade is required by this change.

`static/literature-account.js` loads official Firebase JS SDK 13.1.0. Web app identifiers are intentionally public. No administrator credential, OAuth client secret, or WeChat secret belongs in this repository.

Private feedback is stored at `readers/{Firebase UID}/feedback/{SHA-256 canonical DOI or article ID}`. The published rules allow only that signed-in UID to read or write its documents, validate fields/types/lengths/signals, require a server timestamp and immutable identity, and deny all other paths and permanent deletion. An empty signal/note document is an undo tombstone. Feedback is not copied to GitHub or the public article payload. Firestore uses its default memory cache; signing out clears the visible feedback and listener.

The rules in `firestore.rules` were published in the Firebase Console on 2026-10-24, after seven passing local Firestore emulator checks covering ownership, anonymous access, injection, validation, timestamps and undo, and retrieved from the published console editor for source control. Security rules are a prototype requiring review before a broader launch.

`For you` uses private signals and the public article history to rank by title/summary similarity and topic overlap. Notes are private reading references, not interpreted by AI. Rankings remain bounded by editorial relevance, retain all articles, and demote an explicitly irrelevant paper. No export/import step is needed. Weekly public surveys remain separate from per-account ranking; the scheduled ChatGPT task does not automatically access private Firestore data.

WeChat remains pending an approved WeChat Open Platform website application and a secure server-side token exchange/custom Firebase token endpoint. AppSecret must never be placed in frontend JavaScript. There is no pretend WeChat login button.

Run ranking tests: `node --test bioe-account/test/personalization.cjs`. Build and verify the site with the existing repository workflow. Actual Google login and cross-tab saving must also be checked in the deployed website before declaring end-to-end verification complete.
