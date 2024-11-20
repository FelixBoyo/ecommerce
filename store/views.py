from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime

from .models import *
from.utils import cookieCart, cartData, guestOrder

from .forms import UserRegistrerForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView


def signup(request):
    if request.method == "POST":
        form = UserRegistrerForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hi {username}, your account has been created successfully!')
            return redirect('store')  # Replace 'store' with the actual URL name you want to redirect to
    else:
        form = UserRegistrerForm()  # Initialize an empty form for GET requests

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def store(request):
    # Handle cart data differently for logged-in and anonymous users
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()  # Get all items for this order
            cartItems = order.get_cart_items  # Get the total number of items in the cart
        except Customer.DoesNotExist:
            # Handle the case where Customer does not exist
            return redirect('error_page')  # Redirect to an error page or show a message
    else:
        # If user is not logged in, get cart data from cookies
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    # Query all products to display in the store
    products = Product.objects.all()
    
    # Context for rendering the template
    context = {'products': products, 'cartItems': cartItems}
    
    # Render the template with the context
    return render(request, 'store/store.html', context)




def cart(request):
    # Handle cart data differently for logged-in and anonymous users
    if request.user.is_authenticated:
        # If user is logged in, get cart data from the database
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()  # Get all items for this order
        cartItems = order.get_cart_items  # Get the total number of items in the cart
    else:
        # If user is not logged in, get cart data from cookies
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    # Context for rendering the template
    context = {'items': items, 'order': order, 'cartItems': cartItems}

    # Render the template with the context
    return render(request, 'store/cart.html', context)



def checkout(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Get the cart data from the database for logged-in users
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()  # Get all items for this order
        cartItems = order.get_cart_items  # Get the total number of items in the cart
    else:
        # Get the cart data from cookies for anonymous users
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    # Context for rendering the template
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    
    # Render the checkout template with the context
    return render(request, 'store/checkout.html', context)
 # Exempt from CSRF for simplicity, but it's better to handle CSRF tokens correctly in production
def updateItem(request):
    # Load the JSON data sent from the frontend
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('Product:', productId)

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # If the user is logged in, update the cart in the database
        customer = request.user.customer
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # Get or create the order item for this order and product
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        # Adjust the quantity based on the action ('add' or 'remove')
        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1

        # Save the order item if the quantity is greater than 0, otherwise delete it
        orderItem.save()
        if orderItem.quantity <= 0:
            orderItem.delete()

    else:
        # If the user is not logged in, update the cart in cookies
        cart = json.loads(request.COOKIES.get('cart', '{}'))

        if action == 'add':
            if productId in cart:
                cart[productId]['quantity'] += 1
            else:
                cart[productId] = {'quantity': 1}
        elif action == 'remove':
            if productId in cart:
                cart[productId]['quantity'] -= 1
                if cart[productId]['quantity'] <= 0:
                    del cart[productId]

        # Save the updated cart back into cookies
        response = JsonResponse('Item was added', safe=False)
        response.set_cookie('cart', json.dumps(cart), max_age=3600)  # Set the cookie to expire in 1 hour
        return response

    # Respond with a JSON success message
    return JsonResponse('Item was added', safe=False)


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)



    else:
        customer, order = guestOrder(request, data)


    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = "True"
    order.save()


    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment complete', safe=False)
