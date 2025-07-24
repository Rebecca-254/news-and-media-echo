from django.urls import path
from . import views

urlpatterns = [
   path('', views.home, name='home'),  # your home view
    # path('dashboard/', views.dashboard, name='dashboard'),
]
