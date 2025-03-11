from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Article, Comment, Profile
import re


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""

    class Meta:
        model = Profile
        fields = ['bio']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True)
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']

    def validate_username(self, value):
        """✅ Ensure username contains no spaces"""
        if " " in value:
            raise serializers.ValidationError(
                "Username cannot contain spaces.")
        return value

    def validate_email(self, value):
        """✅ Ensure the email is in a valid format"""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_password(self, value):
        """✅ Ensure password has at least 8 characters and one uppercase letter"""
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter.")
        return value

    def create(self, validated_data):
        """Create user and profile"""
        profile_data = validated_data.pop('profile', {})
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        Profile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        """Update user and profile"""
        profile_data = validated_data.pop('profile', None)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        if profile_data:
            profile = instance.profile
            profile.bio = profile_data.get('bio', profile.bio)
            profile.save()

        instance.save()
        return instance


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for articles"""
    author = UserSerializer(read_only=True)
    total_likes = serializers.IntegerField(
        source="likes.count", read_only=True)
    total_favorites = serializers.IntegerField(
        source="favorited_by.count", read_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(), required=False, default=list)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'created_at',
                  'updated_at', 'total_likes', 'total_favorites', 'tags']

    def create(self, validated_data):
        """Handle tag processing before creating an article"""
        tags = validated_data.pop('tags', [])
        article = Article.objects.create(**validated_data, tags=tags)
        return article

    def update(self, instance, validated_data):
        """Handle tag processing when updating an article"""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags = tags

        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    user = UserSerializer(read_only=True)
    article = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(), required=False)

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'content', 'created_at']
