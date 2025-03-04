from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Article, Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        """Override create to handle password securely"""
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            is_active=True  # Ensure the user is active so they can log in
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user


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
