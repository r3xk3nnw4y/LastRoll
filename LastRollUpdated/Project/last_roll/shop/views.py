from django.shortcuts import render
from django.http import HttpResponse

posts = [ 
    {
    'author': 'John Doe',
    'title': 'Test Post 1',
    'content': 'Filler'
    },
    {
    'author': 'Jane Doe',
    'title': 'Test Post 2',
    'content': 'Filler 2'
    }
]

def home(request):
    context = {
        'posts': posts,
        'title': 'Last Roll Home'
    }
    return render(request, 'shop/home.html', context)

    
def about(request):
    context = {
        'posts': posts,
        'title': 'About'
    }
    return render(request, 'shop/about.html', context)
    
def login(request):
    context = {
        'title': 'Log In'
    }
    return render(request, 'shop/login.html', context)
    
def register(request):
    context = {
        'title': 'Register'
    }
    return render(request, 'shop/register.html', context)
    
    


