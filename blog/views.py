from rest_framework import generics, permissions
from .models import Article, Comment
from .serializers import ArticleSerializer, CommentSerializer


class ArticleListCreateView(generics.ListCreateAPIView):
    """View to list all articles and create a new article"""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, and delete a specific article"""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CommentListCreateView(generics.ListCreateAPIView):
    """View to list all comments for an article and create a new comment"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Return comments related to a specific article"""
        article_id = self.kwargs['article_id']
        return Comment.objects.filter(article_id=article_id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentDetailView(generics.RetrieveDestroyAPIView):
    """View to retrieve and delete a specific comment"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
