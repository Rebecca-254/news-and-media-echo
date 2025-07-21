from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django.views import View
from .models import Article, Category, Comment, Reaction, Newsletter, Tag
from .forms import CommentForm, NewsletterForm, SearchForm

class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        return Article.objects.filter(
            is_published=True
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['featured_articles'] = Article.objects.filter(
            is_published=True, 
            is_featured=True
        ).select_related('author', 'category')[:3]
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'
    
    def get_object(self):
        article = get_object_or_404(
            Article.objects.select_related('author', 'category').prefetch_related('tags'),
            slug=self.kwargs['slug'],
            is_published=True
        )
        # Increment view count
        article.increment_views()
        return article
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Comments
        comments = Comment.objects.filter(
            article=article,
            is_approved=True,
            parent=None
        ).select_related('author').prefetch_related('replies__author')
        
        context['comments'] = comments
        context['comment_form'] = CommentForm()
        
        # Related articles
        context['related_articles'] = Article.objects.filter(
            category=article.category,
            is_published=True
        ).exclude(id=article.id).select_related('author')[:4]
        
        # User reaction if authenticated
        if self.request.user.is_authenticated:
            try:
                context['user_reaction'] = Reaction.objects.get(
                    article=article,
                    user=self.request.user
                )
            except Reaction.DoesNotExist:
                context['user_reaction'] = None
        
        # Reaction counts
        context['reaction_counts'] = Reaction.objects.filter(
            article=article
        ).values('reaction_type').annotate(count=Count('reaction_type'))
        
        return context

class CategoryDetailView(ListView):
    model = Article
    template_name = 'news/category_detail.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Article.objects.filter(
            category=self.category,
            is_published=True
        ).select_related('author').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        return context

class TagDetailView(ListView):
    model = Article
    template_name = 'news/tag_detail.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Article.objects.filter(
            tags=self.tag,
            is_published=True
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context

class SearchView(ListView):
    model = Article
    template_name = 'news/search_results.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Article.objects.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) | 
                Q(excerpt__icontains=query),
                is_published=True
            ).select_related('author', 'category').distinct()
        return Article.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.article = get_object_or_404(
            Article, 
            slug=self.kwargs['slug'],
            is_published=True
        )
        
        # Handle reply to parent comment
        parent_id = self.request.POST.get('parent_id')
        if parent_id:
            form.instance.parent = get_object_or_404(Comment, id=parent_id)
        
        messages.success(self.request, 'Your comment has been added!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.article.get_absolute_url()

# AJAX Views
@method_decorator(csrf_exempt, name='dispatch')
class ReactionView(LoginRequiredMixin, View):
    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug, is_published=True)
        
        try:
            data = json.loads(request.body)
            reaction_type = data.get('reaction_type')
        except:
            return JsonResponse({'error': 'Invalid data'}, status=400)
        
        if reaction_type not in dict(Reaction.REACTION_TYPES).keys():
            return JsonResponse({'error': 'Invalid reaction type'}, status=400)
        
        reaction, created = Reaction.objects.get_or_create(
            article=article,
            user=request.user,
            defaults={'reaction_type': reaction_type}
        )
        
        if not created:
            if reaction.reaction_type == reaction_type:
                # Remove reaction if same type
                reaction.delete()
                return JsonResponse({'status': 'removed'})
            else:
                # Update reaction type
                reaction.reaction_type = reaction_type
                reaction.save()
        
        # Get updated reaction counts
        reaction_counts = {}
        for r_type, _ in Reaction.REACTION_TYPES:
            count = Reaction.objects.filter(
                article=article,
                reaction_type=r_type
            ).count()
            reaction_counts[r_type] = count
        
        # Update article likes count (sum of all reactions)
        article.likes_count = sum(reaction_counts.values())
        article.save()
        
        return JsonResponse({
            'status': 'success',
            'reaction_type': reaction_type,
            'reaction_counts': reaction_counts,
            'likes_count': article.likes_count
        })

class NewsletterSubscribeView(View):
    def post(self, request):
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            
            if not created:
                newsletter.is_active = True
                newsletter.save()
            
            messages.success(request, 'Thank you for subscribing to our newsletter!')
            return redirect('core:home')
        
        messages.error(request, 'Invalid email address')
        return redirect('core:home') 