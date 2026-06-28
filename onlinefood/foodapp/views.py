import hashlib
import hmac
import base64
import uuid
from datetime import datetime

from django.contrib import messages
import random
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .models import Cart, CartItems, Item, OrderPlaced
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.conf import settings

# Create your views here.
def home(request):
    queryset = list(Item.objects.all())
    featured_items = random.sample(queryset, min(len(queryset), 4))
    context = {"featured_items": featured_items}

    queryset = Item.objects.all()

    if request.GET.get("search"):
        queryset = queryset.filter(item_name__icontains = request.GET.get("search"))

        context = {"items": queryset}

        return render(request, "items.html", context)

    return render(request, "home.html", context)


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, "Invalid Username.")
            return redirect('/')
        
        user = authenticate(username = username, password = password)

        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/')
        else:
            login(request, user)
            return redirect('/')
    return render(request, 'login.html')

def logout_page(request):
    logout(request)
    return redirect('/')

def register(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.filter(username = username)

        if user.exists():
            messages.info(request, "Username already taken.")
            return redirect("/register/") 

        user = User.objects.create(
            first_name= first_name, 
            last_name= last_name,
            username= username, 
        )

        user.set_password(password)
        user.save()
        messages.info(request, "Account created successfully")
        return redirect("/register/")

    return render(request, "register.html")
    
@require_POST
@login_required(login_url= "/login/")
def add_cart(request, item_uid):
    user = request.user
    item_obj = Item.objects.get(uid = item_uid)
    cart , created = Cart.objects.get_or_create(user= user, is_paid = False)

    cart_items , created = CartItems.objects.get_or_create(
        cart = cart,
        item = item_obj,
    )

    if not created:
        cart_items.quantity += 1
        cart_items.save()
    else:
        cart_items.save()                       
                                          
    return redirect('/')

@login_required(login_url= "/login/")
def cart(request):
    try:
        cart = Cart.objects.get(is_paid=False,user= request.user)
        cartItems = CartItems.objects.filter(cart = cart)
        if not cartItems.exists():
            context = {'carts' : cart,'cart_items':None, 'total_amount':None}
        else:
            total_amount = cart.get_cart_total()
            if total_amount is None:
                context = {'carts' : cart,'cart_items':cartItems, 'total_amount': None}
            else:
                tax_amount = int(total_amount * settings.ESEWA_TAX_RATE / 100)
                total_amount = total_amount + tax_amount
                transaction_uuid = str(uuid.uuid4())
                signature_data = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={settings.ESEWA_PRODUCT_CODE}"
                signature = base64.b64encode(
                    hmac.new(
                        settings.ESEWA_SECRET_KEY.encode(),
                        signature_data.encode(),
                        hashlib.sha256,
                    ).digest()
                ).decode()

                context = {
                    'carts': cart,
                    'cart_items': cartItems,
                    'total_amount': total_amount,
                    'tax_amount': tax_amount,
                    'transaction_uuid': transaction_uuid,
                    'signature': signature,
                    'esewa_product_code': settings.ESEWA_PRODUCT_CODE,
                    'esewa_success_url': settings.ESEWA_SUCCESS_URL,
                    'esewa_failure_url': settings.ESEWA_FAILURE_URL,
                }
    except Cart.DoesNotExist:
        context = {'carts' : None,'cart_items':None, 'total_amount':None}
    

    return render(request, 'cart.html', context)

@require_POST
@login_required(login_url= "/login/")
def remove_cart_items(request, cart_item_uid):
    try:
        CartItems.objects.get(uid = cart_item_uid).delete()
        return redirect('/cart/')
    except Exception as e:
        print(e)

@login_required(login_url= "/login/")
def orders(request):
    orders = Cart.objects.filter(is_paid=True, user=request.user)
    context = {'orders': orders}
    return render(request, 'orders.html', context)

@login_required(login_url= "/login/")
def add_item(request):
    if request.method == "POST":
        data = request.POST

        item_name = data.get("item_name")
        description = data.get("description")
        category= data.get("category")
        price = data.get("price")
        image = request.FILES.get("image")
        
        Item.objects.create(
            item_name = item_name,
            description = description,
            category = category,
            price = price,
            image = image,
        )

        return redirect('/all-items/')
    
    return render(request, 'add_item.html')
    

def all_items(request):
    queryset = Item.objects.all().order_by('-created_at')

    if request.GET.get("search"):
        queryset = queryset.filter(item_name__icontains=request.GET.get("search"))

    paginator = Paginator(queryset, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"items": page_obj, "page_obj": page_obj}
    return render(request, "items.html", context)

@require_POST
@login_required(login_url= "/login/")
def delete_item(request, item_uid):
    queryset = Item.objects.get(uid = item_uid)
    queryset.delete()
    return redirect("/all-items/")

@login_required(login_url= "/login/")
def update_item(request, item_uid):
    queryset = Item.objects.get(uid = item_uid)

    if request.method == "POST":
        data = request.POST
        item_name = data.get("item_name")
        description = data.get("description")
        category = data.get("category")
        price = data.get("price")
        image = request.FILES.get("image")
        

        queryset.item_name = item_name
        queryset.description = description
        queryset.category = category
        queryset.price = price
        if image:
            queryset.image = image

        queryset.save()
        return redirect("/all-items/")

    context = {"item" : queryset}
    return render(request, "update_items.html", context)

@login_required(login_url="/login/")
def success(request):
    data = request.GET.get('data')
    if not data:
        messages.error(request, "Invalid payment response.")
        return redirect('/cart/')

    try:
        decoded = base64.b64decode(data).decode()
        import json
        payment_info = json.loads(decoded)
        if payment_info.get('status') != 'COMPLETE':
            messages.error(request, "Payment was not completed.")
            return redirect('/cart/')

        transaction_uuid = payment_info.get('transaction_uuid')
        cart = Cart.objects.get(user=request.user, is_paid=False)
        cart.is_paid = True
        cart.save()

        for cart_item in cart.cart_item.all():
            OrderPlaced.objects.create(
                user=request.user,
                item=cart_item.item,
                quantity=cart_item.quantity,
            )

        messages.success(request, "Payment successful!")
        return render(request, "success.html")
    except Exception as e:
        messages.error(request, f"Payment verification failed: {e}")
        return redirect('/cart/')

def all_orders(request):
    orders = Cart.objects.filter(is_paid=True)
    context = {'orders': orders}
    return render(request, 'all_orders.html', context)


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)