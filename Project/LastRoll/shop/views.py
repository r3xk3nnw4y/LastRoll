from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone


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

@login_required
def role_redirect(request):
    """Redirect user to correct dashboard based on their role."""
    profile = request.user.profile

    if profile.role == profile.ROLE_ADMIN:
        return redirect('shop-admindashboard')
    elif profile.role == profile.ROLE_SELLER:
        return redirect('shop-sellerdashboard')
    else:
        return redirect('shop-buyerhome')

def home(request):
    # If user is already logged in → redirect to their role dashboard
    if request.user.is_authenticated:
        profile = request.user.profile

        if profile.role == profile.ROLE_ADMIN:
            return redirect('shop-admindashboard')
        elif profile.role == profile.ROLE_SELLER:
            return redirect('shop-sellerdashboard')
        else:
            return redirect('shop-buyerhome')

    # Otherwise → show the normal public homepage
    posts = [
        {'author': 'John Doe', 'title': 'First Post', 'content': 'Welcome to Last Roll!', 'date_posted': '2025-10-18'},
        {'author': 'Jane Smith', 'title': 'Second Post', 'content': 'Shop smart with us!', 'date_posted': '2025-10-17'},
    ]

    return render(request, 'shop/home.html', {'posts': posts})

    
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

@login_required
def buyerhome(request):
    """Buyer dashboard — only for users with Buyer role."""
    profile = request.user.profile

    # Restrict access by role
    if profile.role != profile.ROLE_BUYER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Pass user info to the template
    context = {
        'username': request.user.username,
    }
    return render(request, 'shop/buyerhome.html', context)
    
@login_required
def cart(request):
    """Shopping Cart — only for Buyer accounts."""
    profile = request.user.profile

    if profile.role != profile.ROLE_BUYER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Placeholder items
    cart_items = [
        {'name': 'Example Item 1', 'price': 19.99, 'quantity': 2},
        {'name': 'Example Item 2', 'price': 9.99, 'quantity': 1},
    ]

    total = sum(item['price'] * item['quantity'] for item in cart_items)

    context = {
        'username': request.user.username,
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'shop/cart.html', context)

@login_required
def buyeraccount(request):
    """Buyer account page — only for users with Buyer role."""
    profile = request.user.profile

    # Restrict access by role
    if profile.role != profile.ROLE_BUYER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Account info for display
    context = {
        'name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
        'username': request.user.username,
        'member_since': request.user.date_joined,
        'payment_method': "N/A",  # Placeholder until you add real payment data
    }

    return render(request, 'shop/buyeraccount.html', context)

def alllistings(request):
    context = {
        'title': 'All Listings'
    }
    return render(request, 'shop/alllistings.html', context)

def featuredlistings(request):
    context = {
        'title': 'Featured Listings'
    }
    return render(request, 'shop/featuredlistings.html', context)

@login_required
def sellerdashboard(request):
    """Main seller dashboard — only accessible to sellers."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    context = {'username': request.user.username}
    return render(request, 'shop/sellerdashboard.html', context)

@login_required
def selleraccount(request):
    """Seller account info page."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    context = {
        'name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
        'username': request.user.username,
        'member_since': request.user.date_joined,
        'store_name': "Example Store Name",
    }
    return render(request, 'shop/selleraccount.html', context)

@login_required
def sellermylistings(request):
    """Seller listings page — manage products."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    context = {
        'username': request.user.username,
        'listings': [
            {'name': 'Example Product 1', 'price': 24.99, 'stock': 10},
            {'name': 'Example Product 2', 'price': 9.99, 'stock': 5},
        ],
    }
    return render(request, 'shop/sellermylistings.html', context)


@login_required
def sellermyorders(request):
    """Seller orders — view incoming orders."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    context = {
        'orders': [
            {'id': 1001, 'buyer': 'JohnDoe', 'items': 3, 'status': 'Processing'},
            {'id': 1002, 'buyer': 'JaneSmith', 'items': 1, 'status': 'Shipped'},
        ]
    }
    return render(request, 'shop/sellermyorders.html', context)

@login_required
def sellersales(request):
    """Sales summary page — basic placeholder."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    context = {
        'sales_summary': {
            'total_orders': 42,
            'total_revenue': 1250.75,
            'pending_shipments': 5,
        }
    }
    return render(request, 'shop/sellersales.html', context)

@login_required
def admindashboard(request):
    """Admin Dashboard — only for Admin users."""
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")
    context = {'username': request.user.username}
    return render(request, 'shop/admindashboard.html', context)

@login_required
def adminaccount(request):
    """Admin Account Page — includes logout."""
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")

    context = {
        'name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
        'username': request.user.username,
        'member_since': request.user.date_joined,
    }

    return render(request, 'shop/adminaccount.html', context)

@login_required
def pendingsellers(request):
    """Placeholder page for pending seller approvals."""
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")
    context = {
        'sellers': [
            {'username': 'new_seller_1', 'store': 'CoffeeCorner'},
            {'username': 'craftycat', 'store': 'Crafty Creations'},
        ]
    }
    return render(request, 'shop/pendingsellers.html', context)


@login_required
def pendinglistings(request):
    """Placeholder page for listings awaiting approval."""
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")
    context = {
        'listings': [
            {'name': 'Wooden Mug', 'seller': 'CoffeeCorner'},
            {'name': 'Handmade Tote', 'seller': 'Crafty Creations'},
        ]
    }
    return render(request, 'shop/pendinglistings.html', context)


@login_required
def reportedlistings(request):
    """Placeholder page for reported listings."""
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")
    context = {
        'reports': [
            {'listing': 'Old Chair', 'reason': 'Inappropriate description', 'reported_by': 'User123'},
            {'listing': 'Broken Vase', 'reason': 'Scam suspicion', 'reported_by': 'Buyer42'},
        ]
    }
    return render(request, 'shop/reportedlistings.html', context)