from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Article, Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for articles"""
    author = UserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content',
                  'author', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'content', 'created_at']
