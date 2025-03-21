from rest_framework import generics, permissions, status, filters, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from .models import Article, Comment, Profile
from .serializers import ArticleSerializer, CommentSerializer, UserSerializer, ProfileSerializer


class CustomTagSearchFilter(filters.BaseFilterBackend):
    """Custom filter to enable searching by tags in JSONField"""

    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(tags__icontains=search_query)
        return queryset


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission class to allow only the article owner to edit or delete"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsCommentOwnerOrReadOnly(permissions.BasePermission):
    """Permission class to allow only the comment owner to delete"""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class ArticleListCreateView(generics.ListCreateAPIView):
    """View to list all articles and create a new article"""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, CustomTagSearchFilter]
    filterset_fields = ['title', 'content']
    search_fields = ['title', 'content']

    def perform_create(self, serializer):
        """Associate the article with the logged-in user"""
        serializer.save(author=self.request.user)


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, and delete a specific article"""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsOwnerOrReadOnly]


class CommentListCreateView(generics.ListCreateAPIView):
    """View to list all comments for an article and create a new comment"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Return comments related to a specific article"""
        article_id = self.kwargs.get('article_id')
        return Comment.objects.filter(article_id=article_id)

    def perform_create(self, serializer):
        """Automatically associate comment with article from URL"""
        article_id = self.kwargs.get('article_id')

        if not article_id:
            raise serializers.ValidationError(
                {"error": "Article ID is missing"})

        try:
            article = Article.objects.get(pk=article_id)
            serializer.save(user=self.request.user, article=article)
        except Article.DoesNotExist:
            raise serializers.ValidationError({"error": "Article not found"})


class CommentDetailView(generics.RetrieveDestroyAPIView):
    """View to retrieve and delete a specific comment"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCommentOwnerOrReadOnly]


class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        """Handle user registration with error handling"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(
                    {"message": "User registered successfully",
                        "user": UserSerializer(user).data},
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response({"error": "Username or email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """API endpoint for retrieving, updating, and deleting the authenticated user's profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the authenticated user's data"""
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """Update the authenticated user's profile"""
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        serializer = ProfileSerializer(
            profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Delete the authenticated user's account"""
        user = request.user
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_article(request, article_id):
    """Allow users to like/unlike an article"""
    try:
        article = Article.objects.get(id=article_id)
        if request.user in article.likes.all():
            article.likes.remove(request.user)
            return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
        else:
            article.likes.add(request.user)
            return Response({"message": "Article liked"}, status=status.HTTP_201_CREATED)
    except Article.DoesNotExist:
        return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, article_id):
    """Allow users to add/remove an article from their favorites"""
    try:
        article = Article.objects.get(id=article_id)
        if request.user in article.favorited_by.all():
            article.favorited_by.remove(request.user)
            return Response({"message": "Article removed from favorites"}, status=status.HTTP_200_OK)
        else:
            article.favorited_by.add(request.user)
            return Response({"message": "Article added to favorites"}, status=status.HTTP_201_CREATED)
    except Article.DoesNotExist:
        return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)


class FavoriteArticlesView(generics.ListAPIView):
    """View to list all articles favorited by the logged-in user"""
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only the articles favorited by the logged-in user"""
        return Article.objects.filter(favorited_by=self.request.user)
