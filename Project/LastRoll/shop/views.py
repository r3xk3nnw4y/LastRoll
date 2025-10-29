from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from store.models import Product
from store.models import Seller
from .forms import ProductForm
import json

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

def listing(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart_from_cookies(request)

    # Check if product already in cart
    quantity_in_cart = cart.get(str(product_id), 0)

    context = {
        'product': product,
        'quantity_in_cart': quantity_in_cart,
        'listing': Product.objects.filter(id = product_id)
    }
    
    return render(request, 'shop/listing.html', context)
    
@login_required
def cart(request):
    """Shopping Cart — only for Buyer accounts."""
    profile = request.user.profile

    if profile.role != profile.ROLE_BUYER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    cart = get_cart_from_cookies(request)
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total = 0

    for product in products:
        quantity = cart[str(product.id)]
        total += product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity,
        })

    total = sum(item['price'] * item['quantity'] for item in cart_items)

    context = {
        'username': request.user.username,
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'shop/cart.html', context)

def add_to_cart(request, product_id):
    cart = get_cart_from_cookies(request)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1

    response = redirect('view_cart')
    save_cart_to_response(response, cart)
    return response

def clear_cart(request):
    response = redirect('view_cart')
    response.delete_cookie('cart')
    return response

def get_cart_from_cookies(request):
    """Retrieve cart dictionary from cookies."""
    cart = {}
    cart_data = request.COOKIES.get('cart')
    if cart_data:
        try:
            cart = json.loads(cart_data)
        except json.JSONDecodeError:
            cart = {}
    return cart

def save_cart_to_response(response, cart):
    """Save cart dictionary as JSON in cookies."""
    response.set_cookie(
        'cart',
        json.dumps(cart),
        max_age=7 * 24 * 60 * 60,  # 1 week
        httponly=True,
        samesite='Lax'
    )
    return response

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
        'title': 'All Listings',
        'listings': Product.objects.filter(status=1)
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
def sellercreatelisting(request):
    """Seller listings page — add products."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        try:
            seller = Seller.objects.get(user=request.user)
        except Seller.DoesNotExist:
            # Handle the case where the user doesn't have a Seller profile yet
            # For now create one if it doesn't exist
            seller = Seller.objects.create(user=request.user)
        form.instance.seller = seller
        if form.is_valid():
            form.save() # This saves the new object to the database
            return redirect('shop-sellerdashboard') # Redirect to a success page or list view
    else:
        form = ProductForm()
    context = {
        'username': request.user.username,
        'form': form
    }
    return render(request, 'shop/sellercreatelisting.html', context)

@login_required
def sellermylistings(request):
    """Seller listings page — manage products."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    listings = Product.objects.filter(seller__user=profile.user)
    context = {
        'username': request.user.username,
        'listings': listings
    }
    return render(request, 'shop/sellermylistings.html', context)

@login_required
def remove_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission.")
    product.delete()
    return redirect('shop-sellermylistings')


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
        'listings': Product.objects.filter(status=0)
    }
    return render(request, 'shop/pendinglistings.html', context)

@login_required
def approve_product(request, pk):
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")
    product = get_object_or_404(Product, pk=pk)
    product.status = 1
    product.save()
    return redirect('shop-pendinglistings')

@login_required
def reject_product(request, pk):
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")
    product = get_object_or_404(Product, pk=pk)
    product.is_approved = 2
    product.save()
    return redirect('shop-pendinglistings')


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