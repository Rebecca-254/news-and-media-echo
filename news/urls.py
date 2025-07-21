from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('<slug:slug>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('<slug:slug>/react/', views.ReactionView.as_view(), name='react'),
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
]