from django.urls import path
from .views import ArticleListCreateView, ArticleDetailView, CommentListCreateView, CommentDetailView

urlpatterns = [
    # Articles endpoints
    path('articles/', ArticleListCreateView.as_view(), name='article-list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),

    # Comments endpoints
    path('articles/<int:article_id>/comments/',
         CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
