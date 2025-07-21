"""
URL configuration for echoes_of_the_world project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Core app (home, about, contact pages)
    path('', include('core.urls')),
    
    # Accounts app (authentication)
    path('accounts/', include('accounts.urls')),
    
    # News app (articles, categories)
    path('news/', include('news.urls')),
    
    # Favicon (optional)
    path('favicon.ico', TemplateView.as_view(template_name='favicon.ico', content_type='image/x-icon')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers (optional)
#handler404 = 'core.views.handler404'
#andler500 = 'core.views.handler500'