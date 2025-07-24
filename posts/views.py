from django.shortcuts import render 
from django.http import HttpResponse

def home(request):
     return render(request, 'home.html')

def home_view(request):
    return render(request, 'home.html')

def dashboard(request):
    return render(request, 'dashboard.html')  # or 'home/home.html'

# Create your views here.
