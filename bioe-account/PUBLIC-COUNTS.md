# Public Like / Useful totals — implementation draft

The target is the existing `bioe-radar` default Standard Firestore database, documented in `README.md`; the live edition could not be reverified because the Firebase CLI is unauthenticated. No new database or Cloud Function is required.

Anonymous visitors subscribe only to `publicReactionCounts`. Each document has exactly `key`, `like`, `useful`, `updatedAt`. Its document ID is the article SHA-256. It contains no reader UID, nickname, email, individual vote or note. The adapter verifies the document ID against the key before displaying the counts. Missing records display zero only after a successful public snapshot; denied/failed reads do not pretend to be zero.

Named `communityReactions` and `reactionEvents` stay authenticated-only. Private feedback and Read Later remain owner-only. Visitors cannot submit reactions. Signed-in readers retain existing nickname tooltips. Counts remain visible after sign-out; all named reactions are cleared.

Each signed-in reaction update atomically writes private feedback, the named reaction, its historical event and the exact public-counter delta. Rules require the public total and corresponding current reaction to update together, reject standalone/replayed/inflated changes, validate both create and update, and deny deletion. Bookmarks do not affect public counts. A new count document cannot be bootstrapped by an already-existing voter; historical reactions must first be backfilled by a trusted administrator.

## Validation status

Passing: production-adapter and UI regression tests cover public-count-only subscriptions when signed out, stripping identity fields, displayed numbers, disabled voting, private bookmarks, account isolation and existing sorting/filter behavior.

Not run: Firestore rules emulator tests. The official emulator JAR download is blocked with `403: Domain forbidden`. The test tools are installed in `/tmp/bioe-public-counts-deps` for this session. Do not deploy the rules until these tests pass. Firebase database listing returns `Failed to authenticate`; there is no authenticated Firebase management session in this environment. No production rule, data or website change has been made for this feature.

I've set up prototype Security Rules to keep the data in Firestore safe. They are designed to be secure for anonymous aggregate reads while keeping reader identities and private feedback restricted and validating atomic counter changes. However, you should review and verify them before broadly sharing your app. If you'd like, I can help you harden these rules.

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
