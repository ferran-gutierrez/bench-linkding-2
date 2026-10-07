---
name: Netscape import URL deduplication
description: Match import entries by normalized URL, update existing user bookmarks instead of duplicating, and skip later duplicate entries within the same file.
targets:
  - bookmarks/services/importer.py
  - bookmarks/tests/test_importer.py
---

- **REQ-1** When importing a Netscape HTML file, an entry whose normalized URL equals an existing bookmark owned by the importing user updates that bookmark (does not create a second row), applying the same field and tag-merge rules as when the file URL string matches the stored URL exactly—for example importing `https://example.com/` when the user already has `https://example.com` updates the existing bookmark and leaves exactly one bookmark for that user.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-2** Normalized URL comparison for import deduplication uses the same `normalize_url` rules as elsewhere in linkding: scheme and host are case-insensitive, trailing slashes on the path are ignored, and query parameters are order-independent—for example `https://example.org/search?a=1&b=2` and `https://example.org/search?b=2&a=1` are treated as the same URL during import.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-3** When the same normalized URL appears more than once in one import file, only the first occurrence in file order is processed; each later occurrence is skipped entirely (no title, description, notes, dates, flags, or tag changes from that entry).
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-4** A skipped in-file duplicate that appears after an earlier entry with the same normalized URL does not add that entry's tags to the bookmark—for example a file whose first entry is `https://example.com` with tag `alpha` and whose second entry is `https://example.com/` with tag `beta` leaves the bookmark with only `alpha` after import.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-5** Each skipped in-file duplicate increments `ImportResult.failed` and does not increment `ImportResult.success`; for a file with four entries where two are later duplicates of earlier normalized URLs, the result reports `total=4`, `success=2`, and `failed=2`.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-6** In-file duplicate detection applies across the whole file regardless of import batch size—for example when the first of three identical normalized URLs is in one batch and the other two are in a later batch, only the first is imported and both later entries count as failed.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-7** Matching an existing bookmark during import considers only bookmarks owned by the importing user; another user's bookmark with the same normalized URL is never updated, and the importer creates or updates only the importing user's bookmark.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-8** All other Netscape import behaviour unchanged by this task continues to work as before (invalid URLs still fail individually, tag creation, private-flag mapping, favicon/preview scheduling, and exact-URL reimport tag append when there is no normalized duplicate in the file).
  `[@test] ../bookmarks/tests/test_importer.py`

## Assumptions

- Existing bookmark lookup during import reuses `Bookmark.query_existing` (normalized URL plus empty-`url_normalized` fallback) rather than exact `url` string equality on the batch query alone.
- In-file deduplication keys entries by `normalize_url(href)` after parsing; entries with invalid URLs that fail validation continue to follow current import error handling and are not treated as normalized duplicates of valid URLs.
- A skipped in-file duplicate does not run tag association or `_copy_bookmark_data` for that entry.
- Out of scope: changing `normalize_url` itself, deduplicating bookmarks outside Netscape HTML import, or adding database unique constraints on `url_normalized`.
