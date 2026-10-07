---
name: Delete tags through REST API
description: Expose DELETE /api/tags/<id>/ with token authentication, ownership-scoped 404 behavior, bookmark-safe removal, and documented API operation.
targets:
  - bookmarks/api/routes.py
  - docs/src/content/docs/api.md
  - bookmarks/tests/test_tags_api.py
---

- **REQ-1** An authenticated `DELETE` request to `/api/tags/<id>/` for a tag owned by the caller removes that tag and responds with HTTP `204 No Content` and an empty response body.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-2** A `DELETE` request to `/api/tags/<id>/` without a valid API token responds with HTTP `401 Unauthorized`, and the tag with that ID is not deleted.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-3** An authenticated `DELETE` to `/api/tags/<id>/` when `<id>` belongs to another user responds with HTTP `404 Not Found`, and that other user's tag row remains in the database unchanged.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-4** An authenticated `DELETE` to `/api/tags/<id>/` when no tag exists with `<id>` responds with HTTP `404 Not Found`.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-5** Deleting a tag through the API never deletes bookmarks: for a bookmark that has tags `alpha-tag` and `beta-tag`, after `DELETE` removes `beta-tag`, the bookmark still exists and its remaining tag names are exactly `alpha-tag` (order among names is not asserted).
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-6** After a successful tag deletion, `GET /api/tags/` for the same authenticated user no longer includes the deleted tag in `results` while other tags (for example `alpha-tag` created before `zulu-tag` is deleted) still appear.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-7** After a successful tag deletion, `GET /api/tags/<id>/` for the deleted tag's ID responds with HTTP `404 Not Found`.
  `[@test] ../bookmarks/tests/test_tags_api.py`

- **REQ-8** The API documentation in `docs/src/content/docs/api.md` under the Tags section documents tag deletion with `DELETE /api/tags/<id>/`, placed alongside the existing list, retrieve, and create tag operations.
  `[@test] ../bookmarks/tests/test_tags_api.py`

## Assumptions

- Tag deletion is implemented on `TagViewSet` using the same DRF pattern as other API resources (for example `BookmarkBundleViewSet`): add `DestroyModelMixin`, rely on the existing owner-scoped `get_queryset`, and call the model's `delete()` without a separate service function unless one already exists for tags.
- Missing tag IDs and other users' tag IDs both surface as `404 Not Found` because detail actions only resolve tags from the authenticated user's queryset, matching bundle and bookmark detail behavior.
- API tests live in a new `bookmarks/tests/test_tags_api.py` module using `LinkdingApiTestCase` and `BookmarkFactoryMixin`, with `Authorization: Token <key>` credentials consistent with existing API tests.
- Documentation follows the same **Delete** subsection style used for bookmarks, assets, and bundles (HTTP method line plus a short description, no new dependencies or settings changes).
