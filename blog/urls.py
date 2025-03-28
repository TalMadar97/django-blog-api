from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ArticleListCreateView, ArticleDetailView,
    CommentListCreateView, CommentDetailView,
    RegisterView, ProfileView, like_article,
    toggle_favorite, FavoriteArticlesView,
    ArticleList, ArticleDetail
)

urlpatterns = [
    # ✅ Authentication Endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ✅ User Profile Management
    path('profile/', ProfileView.as_view(), name='profile'),

    # ✅ Article Management
    path('articles/', ArticleList.as_view(), name='article-list'),
    path('articles/<int:pk>/', ArticleDetail.as_view(), name='article-detail'),
    path('articles/<int:article_id>/like/', like_article, name='like-article'),

    # ✅ Favorite Articles
    path('articles/<int:article_id>/favorite/',
         toggle_favorite, name='toggle-favorite'),
    path('articles/favorites/', FavoriteArticlesView.as_view(),
         name='favorite-articles'),

    # ✅ Comment Management
    path('articles/<int:article_id>/comments/',
         CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
