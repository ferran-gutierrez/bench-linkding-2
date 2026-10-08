---
name: Netscape import deduplicates by normalized URL
description: Netscape HTML import treats bookmarks as the same URL when normalized forms match, updates existing user bookmarks instead of creating duplicates, and skips later duplicate entries within the file.
targets:
  - bookmarks/services/importer.py
  - bookmarks/tests/test_importer.py
---

- **REQ-1** When importing Netscape HTML, an entry whose `normalize_url(href)` equals the normalized URL of an existing bookmark owned by the importing user updates that bookmark (does not create a second row), for example importing `https://example.com` when the user already has `https://example.com/`.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-2** When an import entry updates an existing bookmark via normalized URL match, field and tag behavior matches exact-URL re-import today: file fields are applied with the same empty-field preservation rules, and tags from the file are added to the bookmark’s existing tags without removing prior tags.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-3** When two or more entries in the same import file share the same normalized URL, only the first entry in file order is processed; each later entry is skipped without changing title, description, notes, or tags, for example file order `https://example.com/` (title “First”) then `https://example.com` (title “Second”) leaves title “First”.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-4** Each entry skipped as an in-file duplicate of an earlier entry increments `ImportResult.failed` and does not increment `ImportResult.success`, while `ImportResult.total` still counts every parsed entry.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-5** For a file with four parsed entries where two entries are in-file duplicates of earlier entries, `import_netscape_html` returns `total=4`, `success=2`, and `failed=2`.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-6** In-file duplicate detection uses normalized URL equality and applies across the full parsed bookmark list (including entries processed in different import batches), so a duplicate appearing after hundreds of other entries is still skipped.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-7** Normalized URL matching for existing bookmarks considers only bookmarks owned by the importing user; another user’s bookmark with the same normalized URL is ignored, and the import creates or updates only the importing user’s bookmark.
  `[@test] ../bookmarks/tests/test_importer.py`

- **REQ-8** Entries that fail validation for other reasons (for example missing or invalid URL) still increment `failed` and behave as before; normalization-based deduplication does not change those outcomes.
  `[@test] ../bookmarks/tests/test_importer.py`

## Assumptions

- URL normalization for import deduplication is the existing `normalize_url` function in `bookmarks/utils.py` (scheme and host case-insensitive, trailing path slashes removed, query parameters sorted); normalization rules are not changed in this task.
- In-file duplicate tracking keys on `normalize_url(entry.href)` for every parsed entry, including entries whose import attempt fails validation, so a later duplicate of an earlier failed entry is still skipped as a duplicate failure.
- Matching an existing bookmark uses the same owner-scoped normalized lookup semantics as `Bookmark.query_existing` (including the fallback when `url_normalized` is empty on stored bookmarks).
- No database migration or new dependencies are required; implementation uses existing fields and in-memory tracking during import.
- Favicon and preview scheduling after import remain unchanged.
