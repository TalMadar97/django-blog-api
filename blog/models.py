from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """Profile model for additional user information"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Article(models.Model):
    """Model for articles"""
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        User, related_name="liked_articles", blank=True)
    favorited_by = models.ManyToManyField(
        User, related_name="favorite_articles", blank=True)
    tags = models.JSONField(default=list, blank=True)

    thumbnail = models.ImageField(
        upload_to="thumbnails/", blank=True, null=True)

    def total_likes(self):
        return self.likes.count()

    def total_favorites(self):
        return self.favorited_by.count()

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Model for comments"""
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"
