from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib import messages
from store.models import SellerApplication, Seller, Product
from .forms import SellerRegisterForm, BuyerRegisterForm, ProductForm
from django.db.models import Q
from django.contrib.auth.models import User

# -------------------- ROLE REDIRECT --------------------

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

# -------------------- BASIC PAGES --------------------

def home(request):
    if request.user.is_authenticated:
        return role_redirect(request)
    posts = [
        {'author': 'John Doe', 'title': 'First Post', 'content': 'Welcome to Last Roll!', 'date_posted': '2025-10-18'},
        {'author': 'Jane Smith', 'title': 'Second Post', 'content': 'Shop smart with us!', 'date_posted': '2025-10-17'},
    ]
    return render(request, 'shop/home.html', {'posts': posts})

def about(request):
    return render(request, 'shop/about.html', {'title': 'About'})

@login_required
def suspension_notice(request):
    """Displays suspension details to the suspended user."""
    profile = request.user.profile
    if not profile.suspended:
        # If the user is no longer suspended, just send them home
        return redirect('shop-home')
    return render(request, 'shop/suspension_notice.html', {'reason': profile.suspension_reason})

# -------------------- BUYER PAGES --------------------

@login_required
def buyerhome(request):
    if request.user.profile.role != request.user.profile.ROLE_BUYER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    return render(request, 'shop/buyerhome.html', {'username': request.user.username})

@login_required
def cart(request):
    if request.user.profile.role != request.user.profile.ROLE_BUYER:
        return HttpResponseForbidden("You do not have permission.")
    cart_items = [
        {'name': 'Example Item 1', 'price': 19.99, 'quantity': 2},
        {'name': 'Example Item 2', 'price': 9.99, 'quantity': 1},
    ]
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def buyeraccount(request):
    if request.user.profile.role != request.user.profile.ROLE_BUYER:
        return HttpResponseForbidden("You do not have permission.")
    context = {
        'name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
        'username': request.user.username,
        'member_since': request.user.date_joined,
    }
    return render(request, 'shop/buyeraccount.html', context)

@login_required
def alllistings(request):
    query = request.GET.get('name', '').strip()
    listings = Product.objects.filter(status=1)  # show all approved listings, even if reported
    if query:
        listings = listings.filter(name__icontains=query)
    return render(request, 'shop/alllistings.html', {'listings': listings, 'query': query})

def featuredlistings(request):
    return render(request, 'shop/featuredlistings.html', {'title': 'Featured Listings'})

# -------------------- SELLER PAGES --------------------

@login_required
def sellerdashboard(request):
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission.")

    app = SellerApplication.objects.filter(user=request.user).first()
    if not app:
        return render(request, 'shop/sellerpending.html', {'message': "No seller application found."})
    if app.status == SellerApplication.STATUS_PENDING:
        return render(request, 'shop/sellerpending.html', {'message': "Awaiting admin approval."})
    if app.status == SellerApplication.STATUS_DENIED:
        return render(request, 'shop/sellerpending.html', {'message': "Application denied."})

    return render(request, 'shop/sellerdashboard.html', {'username': request.user.username})

@login_required
def selleraccount(request):
    if request.user.profile.role != request.user.profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission.")
    seller = Seller.objects.filter(user=request.user).first()
    context = {
        'username': request.user.username,
        'email': request.user.email,
        'store_name': seller.store_name if seller else 'N/A',
        'location': seller.location if seller else 'N/A',
        'description': seller.description if seller else 'N/A',
    }
    return render(request, 'shop/selleraccount.html', context)

@login_required
def sellercreatelisting(request):
    if request.user.profile.role != request.user.profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission.")
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            seller, _ = Seller.objects.get_or_create(user=request.user)
            product = form.save(commit=False)
            product.seller = seller
            product.save()
            return redirect('shop-sellerdashboard')
    else:
        form = ProductForm()
    return render(request, 'shop/sellercreatelisting.html', {'form': form})

@login_required
def sellermylistings(request):
    if request.user.profile.role != request.user.profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission.")
    listings = Product.objects.filter(seller__user=request.user)
    return render(request, 'shop/sellermylistings.html', {'listings': listings})

@login_required
def sellermyorders(request):
    """Seller orders — view incoming orders."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Placeholder order data
    context = {
        'orders': [
            {'id': 1001, 'buyer': 'JohnDoe', 'items': 3, 'status': 'Processing'},
            {'id': 1002, 'buyer': 'JaneSmith', 'items': 1, 'status': 'Shipped'},
        ]
    }
    return render(request, 'shop/sellermyorders.html', context)

@login_required
def sellersales(request):
    """View total sales data for the seller."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Placeholder data — you can replace this with actual DB logic later
    context = {
        'sales_summary': {
            'total_sales': 15,
            'total_revenue': 1240.50,
            'top_product': 'Metal D20 Set',
        },
        'recent_sales': [
            {'id': 1, 'product': 'Wood D6 Set', 'amount': 40.00, 'date': '2025-10-25'},
            {'id': 2, 'product': 'Glass Dice Set', 'amount': 75.00, 'date': '2025-10-24'},
        ],
    }
    return render(request, 'shop/sellersales.html', context)


@login_required
def remove_product(request, pk):
    if request.user.profile.role != request.user.profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission.")
    get_object_or_404(Product, pk=pk, seller__user=request.user).delete()
    return redirect('shop-sellermylistings')

# -------------------- ADMIN PAGES --------------------

@login_required
def admindashboard(request):
    if request.user.profile.role != request.user.profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission.")
    return render(request, 'shop/admindashboard.html')

@login_required
def adminaccount(request):
    """Admin Account Page — includes logout."""
    profile = request.user.profile

    # Restrict to admins only
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
def pendinglistings(request):
    if request.user.profile.role != request.user.profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission.")
    listings = Product.objects.filter(status=0)
    return render(request, 'shop/pendinglistings.html', {'listings': listings})

@login_required
def approve_product(request, pk):
    if request.user.profile.role != request.user.profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission.")
    product = get_object_or_404(Product, pk=pk)
    product.status = 1
    product.save()
    return redirect('shop-pendinglistings')

@login_required
def reject_product(request, pk):
    if request.user.profile.role != request.user.profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission.")
    product = get_object_or_404(Product, pk=pk)
    product.status = 2
    product.save()
    return redirect('shop-pendinglistings')

@login_required
def pendingsellers(request):
    if request.user.profile.role != request.user.profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission.")
    pending_apps = SellerApplication.objects.filter(status=SellerApplication.STATUS_PENDING)
    return render(request, 'shop/pendingsellers.html', {'sellers': pending_apps})

@require_POST
@login_required
def update_seller_status(request, seller_id):
    if request.user.profile.role != request.user.profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission.")
    app = get_object_or_404(SellerApplication, id=seller_id)
    action = request.POST.get('action')

    if action == 'approve':
        app.status = SellerApplication.STATUS_APPROVED
        app.save()
        seller, _ = Seller.objects.get_or_create(user=app.user)
        seller.store_name = app.store_name
        seller.location = app.location
        seller.description = app.description
        seller.save()
    elif action == 'deny':
        app.status = SellerApplication.STATUS_DENIED
        app.save()
    return redirect('shop-pendingsellers')

@login_required
def manage_users(request):
    """Admin panel — view/search/filter users."""
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")

    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '')

    # Fetch all users except admins
    users = User.objects.filter(profile__role__in=[profile.ROLE_BUYER, profile.ROLE_SELLER])

    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    if role_filter:
        users = users.filter(profile__role=role_filter)

    return render(request, 'shop/manage_users.html', {
        'users': users,
        'query': query,
        'role_filter': role_filter,
    })

@login_required
def toggle_suspension(request, user_id):
    """Suspend or unsuspend a user."""
    admin_profile = request.user.profile
    if admin_profile.role != admin_profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to perform this action.")

    user = get_object_or_404(User, id=user_id)
    target_profile = user.profile

    if request.method == 'POST':
        # Toggle suspension
        suspend = request.POST.get('suspend') == 'true'
        reason = request.POST.get('reason', '').strip()

        target_profile.suspended = suspend
        target_profile.suspension_reason = reason if suspend else ''
        target_profile.save()

    return redirect('shop-manage-users')

# -------------------- REPORT SYSTEM --------------------

@login_required
def report_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user.profile.role != request.user.profile.ROLE_BUYER:
        return HttpResponseForbidden("Only buyers can report listings.")
    product.is_reported = True
    product.save()
    messages.info(request, f"'{product.name}' has been reported for review.")
    return redirect('shop-alllistings')

@login_required
def reportedlistings(request):
    """Admin page — shows only active, unresolved reports."""
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Preload seller relationships for performance
    reports = (
        Product.objects
        .filter(is_reported=True, report_confirmed=False)
        .select_related('seller', 'seller__user')
    )

    context = {'reports': reports}
    return render(request, 'shop/reportedlistings.html', context)


@login_required
def resolve_report(request, pk, action):
    if request.user.profile.role != request.user.profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission.")
    product = get_object_or_404(Product, pk=pk)
    if action == "confirm":
        product.report_confirmed = True
        product.status = 2
    elif action == "dismiss":
        product.is_reported = False
        product.report_confirmed = False
    product.save()
    return redirect('shop-reportedlistings')

# -------------------- REGISTRATION --------------------

def buyerregister(request):
    if request.method == 'POST':
        form = BuyerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            user.profile.role = user.profile.ROLE_BUYER
            user.profile.save()
            login(request, user)
            return redirect('shop-buyerhome')
    else:
        form = BuyerRegisterForm()
    return render(request, 'shop/buyerregister.html', {'form': form})

def sellerregister(request):
    if request.method == 'POST':
        form = SellerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            user.profile.role = user.profile.ROLE_SELLER
            user.profile.save()
            SellerApplication.objects.create(
                user=user,
                store_name=form.cleaned_data['store_name'],
                location=form.cleaned_data['location'],
                description=form.cleaned_data['description']
            )
            login(request, user)
            return redirect('shop-sellerdashboard')
    else:
        form = SellerRegisterForm()
    return render(request, 'shop/sellerregister.html', {'form': form})

def register(request):
    return render(request, 'shop/register.html')