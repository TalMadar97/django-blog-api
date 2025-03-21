from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Article, Comment, Profile


class BlogAPITestCase(APITestCase):
    """Test cases for the Blog API"""

    def setUp(self):
        """Create test user and authentication"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        # Get access token for authentication
        response = self.client.post(
            "/api/token/", {"username": "testuser", "password": "testpass123"}
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Create a test article
        self.article = Article.objects.create(
            title="Test Article", content="Test content", author=self.user, tags=["Python", "Django"]
        )

    def test_register_user_creates_profile(self):
        """Test user registration creates a profile"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "profile": {"bio": "I love testing!"}
        }
        response = self.client.post("/api/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Profile.objects.filter(
            user__username="newuser").exists())

    def test_get_user_profile(self):
        """Test retrieving the user profile"""
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("profile", response.data)

    def test_update_user_profile_with_avatar(self):
        """Test updating user profile with an avatar"""
        avatar = SimpleUploadedFile(
            "avatar.jpg", b"file_content", content_type="image/jpeg")
        data = {"bio": "Updated Bio", "avatar": avatar}
        response = self.client.put("/api/profile/", data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Profile.objects.get(
            user=self.user).bio, "Updated Bio")

    def test_create_article_with_thumbnail(self):
        """Test creating an article with a thumbnail"""
        thumbnail = SimpleUploadedFile(
            "thumbnail.jpg", b"file_content", content_type="image/jpeg")
        data = {
            "title": "Article with Thumbnail",
            "content": "Content",
            "tags": ["Tech"],
            "thumbnail": thumbnail
        }
        response = self.client.post("/api/articles/", data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("thumbnail", response.data)

    def test_update_article_thumbnail(self):
        """Test updating an article's thumbnail"""
        thumbnail = SimpleUploadedFile(
            "new_thumbnail.jpg", b"new_content", content_type="image/jpeg")
        data = {"thumbnail": thumbnail}
        response = self.client.put(
            f"/api/articles/{self.article.id}/", data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_user(self):
        """Test user registration"""
        data = {"username": "newuser", "email": "newuser@example.com",
                "password": "newpassword123"}
        response = self.client.post("/api/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        """Test user login"""
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post("/api/token/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_create_article(self):
        """Test creating an article with tags"""
        data = {
            "title": "New Article",
            "content": "New article content",
            "tags": ["Tech", "Python"]
        }
        response = self.client.post("/api/articles/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            sorted(response.data["tags"]), sorted(["Tech", "Python"]))

    def test_get_articles(self):
        """Test retrieving articles"""
        response = self.client.get("/api/articles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_search_articles_by_tags(self):
        """Test searching articles by tags"""
        response = self.client.get("/api/articles/?search=Python")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        found = any("Python" in article["tags"] for article in response.data)
        self.assertTrue(found, "Tag search did not return expected results")

    def test_update_article(self):
        """Test updating an article"""
        data = {"title": "Updated Title",
                "content": "Updated Content", "tags": ["UpdatedTag"]}
        response = self.client.put(f"/api/articles/{self.article.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title")
        self.assertEqual(sorted(response.data["tags"]), sorted(["UpdatedTag"]))

    def test_delete_article(self):
        """Test deleting an article"""
        response = self.client.delete(f"/api/articles/{self.article.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_comment(self):
        """Test adding a comment to an article"""
        data = {"content": "Great article!"}
        response = self.client.post(
            f"/api/articles/{self.article.id}/comments/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_like_article(self):
        """Test liking an article"""
        response = self.client.post(f"/api/articles/{self.article.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Article liked", response.data["message"])

    def test_unlike_article(self):
        """Test unliking an article"""
        self.client.post(f"/api/articles/{self.article.id}/like/")
        response = self.client.post(f"/api/articles/{self.article.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Like removed", response.data["message"])

    def test_favorite_article(self):
        """Test adding an article to favorites"""
        response = self.client.post(
            f"/api/articles/{self.article.id}/favorite/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Article added to favorites", response.data["message"])

    def test_unfavorite_article(self):
        """Test removing an article from favorites"""
        self.client.post(f"/api/articles/{self.article.id}/favorite/")
        response = self.client.post(
            f"/api/articles/{self.article.id}/favorite/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Article removed from favorites",
                      response.data["message"])

    def test_get_favorite_articles(self):
        """Test retrieving favorite articles"""
        self.client.post(f"/api/articles/{self.article.id}/favorite/")
        response = self.client.get("/api/articles/favorites/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
