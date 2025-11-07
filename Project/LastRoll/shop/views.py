from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from .forms import BuyerRegisterForm, SellerRegisterForm
from store.models import SellerApplication
from django.contrib.auth import login
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from store.models import Product
from store.models import Seller
from store.models import Buyer
from .forms import ProductForm
from .forms import OrderForm
from store.models import Order
from store.models import OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
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
    
def log_in(request):
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
def suspension_notice(request):
    """Displays suspension details to the suspended user."""
    profile = request.user.profile
    if not profile.suspended:
        # If the user is no longer suspended, just send them home
        return redirect('shop-home')
    return render(request, 'shop/suspension_notice.html', {'reason': profile.suspension_reason})

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
        'listing': Product.objects.filter(id = product_id).first()
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

    #total = 0

    context = {
        'username': request.user.username,
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'shop/cart.html', context)

def add_to_cart(request, product_id):
    cart = get_cart_from_cookies(request)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1

    response = redirect('cart')
    save_cart_to_response(response, cart)
    return response

def clear_cart(request):
    response = redirect('cart')
    response.delete_cookie('cart')
    return response

#-------------------------------------------------

def process_order(request):
    cart = get_cart_from_cookies(request)
    products = Product.objects.filter(id__in=cart.keys())
    redirbool = False

    if not products:
        return redirect('view_cart')

    if request.method != "POST":
        return redirect('checkout')

    form = OrderForm(request.POST)
    if not form.is_valid():
        # If invalid, re-render checkout page with errors
        return render(request, 'shop/checkout.html', {
            'form': form,
            'cart_items': [{'product': p, 'quantity': cart[str(p.id)]} for p in products],
            'total': sum(p.price * cart[str(p.id)] for p in products),
        })

    address = form.cleaned_data['address']
    payment = form.cleaned_data['payment']

    #throw error if payment isnt valid here
    if payment not in ['VALID', 'TESTING', '000']:
        messages.error(request, "Invalid payment code. Please choose another.")
        return redirect('checkout')


    for product in products:
        qty = cart[str(product.id)]
        if product.stock < qty:
            qty = product.stock
            redirbool = True
        #if qty == 0:
            #cart[str(product.id)] = cart.popitem(str(product.id), 0)

        #subtotal = product.price * qty
    if redirbool:
        response = redirect('checkout')
        save_cart_to_response(response, cart)
        messages.error(request, "Insufficient stock. Your cart has downsized to available stock, please confirm your purchase.")
        return response

    subtotal = sum(p.price * cart[str(p.id)] for p in products)
    total = subtotal

    order = Order.objects.create(
        buyer=request.user.buyer,
        address=address,
        payment=payment,
        total=total,
    )

    for product in products:
        qty = cart[str(product.id)]
        if product.stock < qty:
            qty = product.stock
        #if qty == 0:
            #cart[str(product.id)] = cart.popitem(str(product.id), 0)
        if qty != 0:
            subtotal = product.price * qty
            OrderItem.objects.create(order=order, product=product, quantity=qty)
            product.stock -= qty
            print(product.seller_id)
            instseller = get_object_or_404(Seller, pk=product.seller_id)
            mastseller = get_object_or_404(Seller, user_id=8)
            print(float(subtotal) * 0.9)
            mastseller.price = float(mastseller.price) + float(subtotal) * 0.1
            instseller.price = float(instseller.price) + float(subtotal) * 0.9
            mastseller.save()
            instseller.save()
            product.save()
    
    response = redirect('shop-home')
    response.delete_cookie('cart')
    return response

   #====================================== 
def checkout(request):
    """Checkout Page — only for Buyer accounts."""
    profile = request.user.profile
    if profile.role != profile.ROLE_BUYER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    cart = get_cart_from_cookies(request)
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total = 0
    redirbool = False

    for product in products:
        quantity = cart[str(product.id)]
        total += product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity,
        })

        instproduct = get_object_or_404(Product, pk=product.pk)
        if instproduct.stock < quantity:
            cart[str(product.id)] = instproduct.stock
            redirbool = True
        #if quantity == 0:
                #cart[str(product.id)]=cart.popitem()
    if redirbool:
        response = redirect('cart')
        save_cart_to_response(response, cart)
        return response

    #Create a form instance (for both GET and POST rendering)
    form = OrderForm()

    context = {
        'username': request.user.username,
        'cart_items': cart_items,
        'total': total,
        'form': form, 
    }
    return render(request, 'shop/checkout.html', context)
#--------------------------------
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
        'payment_method': "N/A",  # Placeholder until payment info exists
    }

    return render(request, 'shop/buyeraccount.html', context)

@login_required
def buyerorders(request):
    """Displays buyer’s orders and refund options."""
    if request.user.profile.role != request.user.profile.ROLE_BUYER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Get Buyer instance
    buyer = Buyer.objects.get(user=request.user)

    # Gather all orders for this buyer
    buyer_orders = Order.objects.filter(buyer=buyer)
    orders = []

    for order in buyer_orders:
        items = [
            {"id": item.product.id, "name": item.product.name, "quantity": item.quantity}
            for item in order.items.all()
        ]
        orders.append({
            "id": order.id,
            "items": items,
            "address": order.address,
            "is_shipped": all(i.is_shipped for i in order.items.all()),
            "is_refunded": any(i.is_refunded for i in order.items.all()),
            "refund_reason": next((i.refund_reason for i in order.items.all() if i.is_refunded), None),
        })

    return render(request, 'shop/buyerorders.html', {'orders': orders})


@login_required
def refund_order(request, order_id):
    """Allow buyers to refund their orders."""
    # Ensure the user is a buyer
    if request.user.profile.role != request.user.profile.ROLE_BUYER:
        return HttpResponseForbidden("You do not have permission to request a refund.")

    # Convert the user → Buyer instance
    buyer = get_object_or_404(Buyer, user=request.user)

    # Ensure the order belongs to this buyer
    order = get_object_or_404(Order, id=order_id, buyer=buyer)

    if request.method == "POST":
        # Get the reason or fallback to default
        reason = request.POST.get("reason", "Buyer requested a refund.")

        # Mark all items as refunded
        for item in order.items.all():
            item.is_refunded = True
            item.refund_reason = reason
            item.save()
            instproduct = get_object_or_404(Product,id=item.product_id)
            print(instproduct.seller_id)
            instseller = get_object_or_404(Seller,id=instproduct.seller_id)
            instseller.price -= instproduct.price
            instseller.save()


        messages.success(request, f"Refund processed for Order #{order.id}")
        return redirect('shop-buyerorders')

    return redirect('shop-buyerorders')


@login_required
def alllistings(request):
    query = request.GET.get('name', '').strip()
    hide_out_of_stock = request.GET.get('hide_out_of_stock', 'off') == 'on'

    listings = Product.objects.filter(status=1)

    if query:
        listings = listings.filter(name__icontains=query)
    if hide_out_of_stock:
        listings = listings.filter(stock__gt=0)

    context = {
        'title': 'All Listings',
        'listings': listings,
        'query': query,
        'hide_out_of_stock': hide_out_of_stock,
    }
    return render(request, 'shop/alllistings.html', context)


def featuredlistings(request):
    context = {
        'title': 'Featured Listings'
    }
    #return redirect('shop-alllisting')
    return render(request, 'shop/featuredlistings.html', context)

@login_required
def sellerdashboard(request):
    """Seller dashboard — only accessible to approved sellers."""
    profile = request.user.profile

    # Must be a seller
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Check for a seller application
    try:
        app = SellerApplication.objects.get(user=request.user)
    except SellerApplication.DoesNotExist:
        return render(request, 'shop/sellerpending.html', {
            'message': "No seller application found. Please contact support."
        })

    # If not yet approved, show waiting screen
    if app.status == SellerApplication.STATUS_PENDING:
        return render(request, 'shop/sellerpending.html', {
            'message': "Your seller account is awaiting admin approval."
        })
    elif app.status == SellerApplication.STATUS_DENIED:
        return render(request, 'shop/sellerpending.html', {
            'message': "Your seller application was denied. Please contact an administrator."
        })

    # If approved, show seller dashboard as usual
    context = {'username': request.user.username}
    return render(request, 'shop/sellerdashboard.html', context)

@login_required
def selleraccount(request):
    """Seller account page — only accessible by approved sellers."""
    profile = request.user.profile

    # Restrict to sellers only
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    try:
        application = SellerApplication.objects.get(user=request.user)
    except SellerApplication.DoesNotExist:
        application = None

    context = {
        'username': request.user.username,
        'email': request.user.email,
        'store_name': getattr(application, 'store_name', 'N/A'),
        'location': getattr(application, 'location', 'N/A'),
        'description': getattr(application, 'description', 'N/A'),
        'status': getattr(application, 'status', 'N/A'),
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
@require_POST
def restock_product(request, product_id):
    """Allows a seller to adjust (increase/decrease) product stock safely."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to restock items.")

    product = get_object_or_404(Product, pk=product_id, seller__user=request.user)

    try:
        change = int(request.POST.get("change", 0))
    except ValueError:
        messages.error(request, "Invalid stock adjustment value.")
        return redirect("shop-sellermylistings")

    new_stock = product.stock + change
    if new_stock < 0:
        messages.error(request, "Stock cannot go below zero.")
    else:
        product.stock = new_stock
        product.save()
        if change > 0:
            messages.success(request, f"Stock increased by {change}. New stock: {product.stock}.")
        elif change < 0:
            messages.warning(request, f"Stock decreased by {-change}. New stock: {product.stock}.")
        else:
            messages.info(request, "No change made to stock.")

    return redirect("shop-sellermylistings")

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
    """Seller orders — view incoming orders, mark shipped, or see refund status."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")

    seller = get_object_or_404(Seller, user=request.user)

    # Pull all order items tied to this seller's products
    order_items = (
        OrderItem.objects.filter(product__seller=seller)
        .select_related('order', 'product', 'order__buyer')
    )

    orders_dict = {}
    for item in order_items:
        order = item.order
        if order.id not in orders_dict:
            orders_dict[order.id] = {
                'id': order.id,
                'buyer': order.buyer.user.username,
                'address': order.address,
                'items': [],
                'is_shipped': False,
                'is_refunded': False,
                'refund_reason': None,
            }

        # Shipping and refund aggregation
        if item.is_shipped:
            orders_dict[order.id]['is_shipped'] = True
        if item.is_refunded:
            orders_dict[order.id]['is_refunded'] = True
            orders_dict[order.id]['refund_reason'] = item.refund_reason

        # Add product to order
        orders_dict[order.id]['items'].append({
            'id': item.product.id,
            'name': item.product.name,
            'quantity': item.quantity,
        })

    context = {
        'orders': list(orders_dict.values()),
        'seller_id': seller.id,
    }

    return render(request, 'shop/sellermyorders.html', context)


@login_required
def sellersales(request):
    """Sales summary page — basic placeholder."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    instseller = get_object_or_404(Seller, user_id=profile.user_id)
    print(profile.user_id)
    context = {
        'sales_summary': {
            'total_orders': 42,
            'total_revenue': instseller.price,
            'pending_shipments': 5,
        }
    }
    return render(request, 'shop/sellersales.html', context)

@login_required
def cashout(request):
    
    """Sales summary page — basic placeholder."""
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    instseller = get_object_or_404(Seller, user_id=profile.id)
    if instseller.price >0:
        instseller.price =0
        messages.success(request, f"the cheque is in the mail")
    else:
        messages.success(request, f"insufficient balance")
    context = {
        'sales_summary': {
            'total_orders': 42,
            'total_revenue': instseller.price,
            'pending_shipments': 5,
        }
    }
    return render(request, 'shop/sellersales.html',context)


@login_required
def mark_orderitems_as_shipped(request, order_pk, seller_pk):
    profile = request.user.profile
    if profile.role != profile.ROLE_SELLER:
        return HttpResponseForbidden("You do not have permission to view this page.")
    order = get_object_or_404(Order, pk=order_pk)
    seller = get_object_or_404(Seller, pk=seller_pk)

    order_items = OrderItem.objects.filter(order=order, product__seller=seller).all()
    for item in order_items:
        item.is_shipped = True
        item.save()
    return redirect('shop-sellermyorders')

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
    """Admin page to review pending sellers."""
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")

    pending_apps = SellerApplication.objects.filter(status=SellerApplication.STATUS_PENDING)
    context = {'sellers': pending_apps}
    return render(request, 'shop/pendingsellers.html', context)

@require_POST
@login_required
def update_seller_status(request, seller_id):
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to perform this action.")

    app = get_object_or_404(SellerApplication, id=seller_id)
    action = request.POST.get('action')

    if action == 'approve':
        app.status = SellerApplication.STATUS_APPROVED
        sellmv = get_object_or_404(Seller,user_id=app.user_id)
        sellmv.location = app.location
        sellmv.description = app.description
        sellmv.store_name = app.store_name
        sellmv.save()

        messages.success(request, f"Seller '{app.store_name}' has been approved.")
    elif action == 'deny':
        app.status = SellerApplication.STATUS_DENIED
        messages.warning(request, f"Seller '{app.store_name}' has been denied.")
    else:
        messages.error(request, "Invalid action.")

    app.save()
    return redirect('shop-pendingsellers')


@login_required
def pendinglistings(request):
    profile = request.user.profile
    if profile.role != profile.ROLE_ADMIN:
        return HttpResponseForbidden("You do not have permission to view this page.")

    listings = (
        Product.objects
        .filter(status=0)
        .select_related('seller', 'seller__user', 'seller__user__sellerapplication')
    )

    return render(request, 'shop/pendinglistings.html', {'listings': listings})


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
    product.status = 2
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

            # Assign seller role
            user.profile.role = user.profile.ROLE_SELLER
            user.profile.save()

            # Create the pending seller application
            SellerApplication.objects.create(
                user=user,
                store_name=form.cleaned_data['store_name'],
                location=form.cleaned_data['location'],
                description=form.cleaned_data['description']
            )

            # Log in the new seller
            login(request, user)

            # Redirect to seller dashboard instead of showing the pending page
            return redirect('shop-sellerdashboard')

    else:
        form = SellerRegisterForm()

    return render(request, 'shop/sellerregister.html', {'form': form})
