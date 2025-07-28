# accounts/urls.py
from django.urls import path
from . import views
from .views import UserPostListView

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Use the function-based dashboard view
    path('my-posts/', UserPostListView.as_view(), name='user_posts'),  # For posts listing
    path('', views.login_view, name='index'),  # Default to login page
]