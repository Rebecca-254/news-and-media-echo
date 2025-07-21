

# Register your models here.
from django.contrib import admin
from .models import Category, Article, Comment, Reaction, Tag, Newsletter

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_published', 'is_featured', 'views_count', 'created_at']
    list_filter = ['status', 'is_published', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Article Info', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('Content', {
            'fields': ('content', 'excerpt', 'featured_image')
        }),
        ('Publishing', {
            'fields': ('status', 'is_published', 'is_featured')
        }),
        ('Stats', {
            'fields': ('views_count', 'likes_count'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new article
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'author', 'is_approved', 'created_at', 'parent']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username', 'article__title']
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = "Disapprove selected comments"

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ['article', 'user', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['article__title', 'user__username']

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']