from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from posts.models import Post
from django.db.models import Sum
from .forms import UserUpdateForm


@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('home')  # Redirect to your home page
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return render(request, 'registration/logged_out.html')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'accounts/profile.html', context)

class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'accounts/dashboard.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
       return Post.objects.filter(author=self.request.user).order_by('-created_at') 


    @login_required
    def dashboard(request):
        # Get all posts by the current user
        user_posts = Post.objects.filter(author=request.user).annotate_comment_count()
        
        # Calculate total views across all posts
        total_views = user_posts.aggregate(total_views=Sum('views'))['total_views'] or 0
        
        # Calculate total comments across all posts
        total_comments = sum(post.comments.count() for post in user_posts)
        
        # Recent activity (customize this based on your activity tracking system)
        recent_activity = [
            {
                'icon': 'plus-circle',
                'color': 'primary',
                'message': 'Created post "How to Build a Django Dashboard"',
                'timestamp': timezone.now() - timezone.timedelta(hours=2)
            },
            {
                'icon': 'chat-left',
                'color': 'info',
                'message': 'Commented on "Django Best Practices"',
                'timestamp': timezone.now() - timezone.timedelta(days=1)
            },
            {
                'icon': 'eye',
                'color': 'success',
                'message': 'Your post got 15 new views',
                'timestamp': timezone.now() - timezone.timedelta(days=2)
            }
        ]
        
        context = {
            'posts': user_posts,
            'total_views': total_views,
            'total_comments': total_comments,
            'recent_activity': recent_activity
        }
        
        return render(request, 'accounts/dashboard.html', context)