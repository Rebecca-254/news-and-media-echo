from django.urls import path
from . import views
from .views import UserPostListView

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', UserPostListView.as_view(), name='dashboard'),
    path('', views.login_view, name='index'), 
    # path('', views.home_view, name='home'), # Default to login page
]