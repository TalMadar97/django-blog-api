from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Article, Comment, Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True)
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']

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


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for articles"""
    author = UserSerializer(read_only=True)
    total_likes = serializers.IntegerField(
        source="likes.count", read_only=True)
    total_favorites = serializers.IntegerField(
        source="favorited_by.count", read_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(), required=False, default=list)

    # ✅ הוספתי שדה תמונת שער למאמרים
    thumbnail = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'created_at',
                  'updated_at', 'total_likes', 'total_favorites', 'tags', 'thumbnail']

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
