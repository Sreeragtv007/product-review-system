
from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProductDetailAPIView, ProductListCreateAPIView, ReviewCreateAPIView, ReviewCreateAPIView, ProductReviewListAPIView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('loginout/', LogoutView.as_view(), name='login'),
    path('products/', ProductListCreateAPIView.as_view(),
         name='product-list-create'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('reviews/', ReviewCreateAPIView.as_view(), name='review-create'),
    path('products/<int:product_id>/reviews/',
         ProductReviewListAPIView.as_view(), name='product-review-list'),
]
