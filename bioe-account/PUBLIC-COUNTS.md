# Public Like / Useful totals

The deployed target is the existing `bioe-radar` default Standard Firestore database, documented in `README.md`. No new database or Cloud Function is required.

Anonymous visitors subscribe only to `publicReactionCounts`. Each document has exactly `key`, `like`, `useful`, `updatedAt`. Its document ID is the article SHA-256. It contains no reader UID, nickname, email, individual vote or note. The adapter verifies the document ID against the key before displaying the counts. Missing records display zero only after a successful public snapshot; denied/failed reads do not pretend to be zero.

Named `communityReactions` and `reactionEvents` stay authenticated-only. Private feedback and Read Later remain owner-only. Visitors cannot submit reactions. Signed-in readers retain existing nickname tooltips. Counts remain visible after sign-out; all named reactions are cleared.

Each signed-in reaction update atomically writes private feedback, the named reaction, its historical event and the exact public-counter delta. Rules require the public total and corresponding current reaction to update together, reject standalone/replayed/inflated changes, validate both create and update, and deny deletion. Bookmarks do not affect public counts. A new count document cannot be bootstrapped by an already-existing voter; historical reactions must first be backfilled by a trusted administrator.

## Validation status

Passing: production-adapter and UI regression tests cover public-count-only subscriptions when signed out, stripping identity fields, displayed numbers, disabled voting, private bookmarks, account isolation and existing sorting/filter behavior.

Verified on 17 November 2026: all 11 Firestore emulator security tests and all 28 adapter, UI, personalization and authentication regression tests passed. The official Firestore emulator v1.22.0 ran with a demo project. The isolated site build, verification of 50 HTML pages, archive checks and account-adapter syntax check passed.

Production rollout completed on 17 November 2026. Firebase CLI compiled and released the rules to the existing `bioe-radar` project. The trusted migration dry-run identified 45 articles, and the applied migration initialized all 45. GitHub PR #1 was merged; Pages workflow run 43999452014 completed successfully.

Live anonymous SDK checks read all 45 aggregate documents and verified the strict four-field schema (24 Like and 35 Useful at verification time). Anonymous reads of communityReactions, reactionEvents and private feedback were denied. Live browser verification showed a signed-in Like increment from 3 to 4, undo back to 3, and signed-out display of Like 3 / Useful 2 with no voter names; the temporary test mark was undone. The verification browser was left signed out.

## Complete validation before rollout

Use an authorized workstation with Node.js 22+, Java 21+, registry access and access to the official Firebase emulator download. Temporary dependencies must stay outside the public checkout:

```sh
npm install --prefix /tmp/bioe-public-counts-deps firebase @firebase/rules-unit-testing firebase-admin firebase-tools
NODE_PATH=/tmp/bioe-public-counts-deps/node_modules /tmp/bioe-public-counts-deps/node_modules/.bin/firebase emulators:exec --only firestore --project demo-bioe-radar --config bioe-account/public-counts-emulator.json 'node --test bioe-account/test/community-rules.cjs'
node --test bioe-account/test/current-feedback.cjs bioe-account/test/personalization.cjs bioe-account/test/google-auth.cjs
```

The emulator cases cover anonymous aggregate get/list, denial of anonymous names/history/private feedback, anonymous writes, unrelated-user writes, missing atomic records, forged timestamps/names, schema injection, oversized values, standalone counters, negative and inflated deltas, two-reader totals, double positives and undo.

## Coordinated production rollout

Do not publish the new client separately from the backend changes: the old rules deny aggregate writes, and the new rules require them. Existing old tabs will need to reload before saving reactions after the rule change.

1. Authenticate Firebase CLI as a project administrator. Confirm the selected project and default database are the existing `bioe-radar` Standard instance. Review and test the draft rules above.
2. Configure Application Default Credentials for the migration through the standard Google authorization flow. Do not put service-account JSON, tokens or live reader data in GitHub or this document.
3. From an authorized terminal, run a dry-run migration first:

```sh
GOOGLE_CLOUD_PROJECT=bioe-radar NODE_PATH=/tmp/bioe-public-counts-deps/node_modules node bioe-account/admin/backfill-public-counts.cjs
```

4. Deploy the tested rules, then initialize historical totals. The migration recomputes current Like/Useful marks from shared reactions only, not private notes or immutable historical events. Each article is updated in a transaction, and rerunning the migration replaces totals rather than adding them again.

```sh
/tmp/bioe-public-counts-deps/node_modules/.bin/firebase deploy --only firestore:rules --project bioe-radar --config bioe-account/public-counts-emulator.json
GOOGLE_CLOUD_PROJECT=bioe-radar NODE_PATH=/tmp/bioe-public-counts-deps/node_modules node bioe-account/admin/backfill-public-counts.cjs --apply
```

5. Build and verify the site, publish the matching frontend, and verify with a signed-out browser: current counts are visible, nickname documents cannot be read, and changing/undoing a signed-in mark changes the corresponding public total exactly once. Keep existing history and preferences intact.

## Not Relevant display update — 17 November 2026

The article controls no longer display a count or voter names for Not Relevant. Its pressed state is read only from the current reader's private feedback. Like and Useful retain their existing count and nickname behavior. This display update does not change deployed Firebase rules or delete historical shared negative records. The separate `feature/public-reaction-counts` branch contains the pending private-only write rules and administrative history-redaction migration; those require backend validation and authorized Firebase deployment before the data-level privacy change is complete.
