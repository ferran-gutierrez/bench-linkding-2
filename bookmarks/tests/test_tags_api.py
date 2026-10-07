from pathlib import Path

from django.urls import reverse
from rest_framework import status

from bookmarks.models import Bookmark, Tag
from bookmarks.tests.helpers import BookmarkFactoryMixin, LinkdingApiTestCase


class TagsApiTestCase(LinkdingApiTestCase, BookmarkFactoryMixin):
    def test_REQ_1_delete_owned_tag_returns_204_and_removes_tag(self):
        self.authenticate()

        tag = self.setup_tag(name="tag-to-delete")

        url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        response = self.delete(url, expected_status_code=status.HTTP_204_NO_CONTENT)

        self.assertEqual(response.content, b"")
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_REQ_2_delete_tag_without_auth_returns_401_and_preserves_tag(self):
        tag = self.setup_tag(name="protected-tag")

        url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.delete(url, expected_status_code=status.HTTP_401_UNAUTHORIZED)

        self.assertTrue(Tag.objects.filter(id=tag.id).exists())

    def test_REQ_3_delete_other_users_tag_returns_404_and_preserves_tag(self):
        self.authenticate()

        other_user = self.setup_user()
        other_tag = self.setup_tag(name="other-user-tag", user=other_user)
        other_tag_id = other_tag.id
        other_tag_name = other_tag.name

        url = reverse("linkding:tag-detail", kwargs={"pk": other_tag.id})
        self.delete(url, expected_status_code=status.HTTP_404_NOT_FOUND)

        other_tag.refresh_from_db()
        self.assertEqual(other_tag.id, other_tag_id)
        self.assertEqual(other_tag.name, other_tag_name)
        self.assertEqual(other_tag.owner_id, other_user.id)

    def test_REQ_4_delete_nonexistent_tag_returns_404(self):
        self.authenticate()

        url = reverse("linkding:tag-detail", kwargs={"pk": 999999})
        self.delete(url, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_REQ_5_delete_tag_leaves_bookmark_with_remaining_tags(self):
        self.authenticate()

        alpha_tag = self.setup_tag(name="alpha-tag")
        beta_tag = self.setup_tag(name="beta-tag")
        bookmark = self.setup_bookmark(tags=[alpha_tag, beta_tag])
        bookmark_id = bookmark.id

        url = reverse("linkding:tag-detail", kwargs={"pk": beta_tag.id})
        self.delete(url, expected_status_code=status.HTTP_204_NO_CONTENT)

        self.assertTrue(Bookmark.objects.filter(id=bookmark_id).exists())
        bookmark.refresh_from_db()
        remaining_names = set(bookmark.tags.values_list("name", flat=True))
        self.assertEqual(remaining_names, {"alpha-tag"})

    def test_REQ_6_deleted_tag_absent_from_list_other_tags_remain(self):
        self.authenticate()

        alpha_tag = self.setup_tag(name="alpha-tag")
        zulu_tag = self.setup_tag(name="zulu-tag")

        delete_url = reverse("linkding:tag-detail", kwargs={"pk": zulu_tag.id})
        self.delete(delete_url, expected_status_code=status.HTTP_204_NO_CONTENT)

        list_url = reverse("linkding:tag-list")
        response = self.get(list_url, expected_status_code=status.HTTP_200_OK)

        result_names = {item["name"] for item in response.data["results"]}
        self.assertNotIn("zulu-tag", result_names)
        self.assertIn("alpha-tag", result_names)
        self.assertIn(alpha_tag.id, {item["id"] for item in response.data["results"]})

    def test_REQ_7_get_detail_after_delete_returns_404(self):
        self.authenticate()

        tag = self.setup_tag(name="deleted-tag")

        delete_url = reverse("linkding:tag-detail", kwargs={"pk": tag.id})
        self.delete(delete_url, expected_status_code=status.HTTP_204_NO_CONTENT)

        self.get(delete_url, expected_status_code=status.HTTP_404_NOT_FOUND)

    def test_REQ_8_api_docs_document_tag_delete(self):
        api_doc_path = Path(__file__).resolve().parents[2] / "docs/src/content/docs/api.md"
        content = api_doc_path.read_text(encoding="utf-8")

        tags_section_start = content.index("### Tags")
        bundles_section_start = content.index("### Bundles")
        tags_section = content[tags_section_start:bundles_section_start]

        self.assertIn("GET /api/tags/", tags_section)
        self.assertIn("GET /api/tags/<id>/", tags_section)
        self.assertIn("POST /api/tags/", tags_section)
        self.assertIn("DELETE /api/tags/<id>/", tags_section)

        create_pos = tags_section.index("POST /api/tags/")
        delete_pos = tags_section.index("DELETE /api/tags/<id>/")
        self.assertGreater(delete_pos, create_pos)
