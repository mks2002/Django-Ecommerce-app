from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm

from django.views import View
from django.views.decorators.cache import never_cache

from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# it is for showing all the products in the testinomials in the main page .....

from django.db.models import OuterRef, Subquery

method_decorator(login_required)
class ProductView(View):
    def get(self, request):
        totalitem = 0
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        grocery = Product.objects.filter(category='GR')

        #   minimum price product from each category ....

        # This query will return the most inexpensive product from each category
        most_inexpensive_products = Product.objects.filter(
            category=OuterRef('category')
        ).order_by('discounted_price')[:1]

        # Final query to get the most inexpensive product from each category
        lowpriceProducts = Product.objects.filter(
            id__in=Subquery(most_inexpensive_products.values('id'))
        ).order_by('?')

        #  maximum price Product from each category ....
        most_expensive_products = Product.objects.filter(
            category=OuterRef('category')
        ).order_by('-discounted_price')[:1]

        # Final query to get the most expensive product from each category
        HighpriceProducts = Product.objects.filter(
            id__in=Subquery(most_expensive_products.values('id'))
        ).order_by('?')

        # this is only vailed for logged in users , so that they can see how many orders are in their carts ....
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(
            request,
            'app/home.html',
            {
                'topwears': topwears,
                'bottomwears': bottomwears,
                'grocery': grocery,
                'totalitem': totalitem,
                # these 2 are for most lowest and highest price product from each category .....
                'lowpriceprod': lowpriceProducts,
                'highpriceprod': HighpriceProducts,
            },
        )


class ProductDetailView(View):

    def get(self, request, pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        print(product.id)
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter( Q(product=product.id) & Q(user=request.user) ).exists()
        return render(
            request,
            'app/productdetail.html',
            {
                'product': product,
                'item_already_in_cart': item_already_in_cart,
                'totalitem': totalitem,
            },
        )

# In Django, if you use the login_required decorator above a view function and a user tries to access that view without being logged in, Django will automatically redirect the user to the login page....


# in the add to cart we use login_required decorator so that if somebody not logged in then he cant able to acess this page and cant able to add Product in the cart....
@login_required()
def add_to_cart(request):
    user = request.user
    item_already_in_cart1 = False
    product_id = request.GET.get('prod_id')
    # if item already in cart then it become true.....
    item_already_in_cart1 = Cart.objects.filter(  Q(product=product_id) & Q(user=request.user) ).exists()
    if item_already_in_cart1 == False:
        product_data = Product.objects.get(id=product_id)
        
        Cart(user=user, product=product_data).save()
        messages.success(request, 'Product Added to Cart Successfully !!')
        return redirect('/cart')
    else:
        return redirect('/cart')
# since in cart table product is a foreign key we have to provide the entire product instance, which is stored in product_data, in place of that field and from there django model automatically save the product_id in the corresponding column but we have to provide the entire product instance if we directly provide the product_id in that column then it gives error......



@login_required
@never_cache
def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        totalamount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        print(cart_product)
        if cart_product:
            for p in cart_product:
                tempamount = p.quantity * p.product.discounted_price
                amount += tempamount
            totalamount = amount + shipping_amount
            return render(
                request,
                'app/addtocart.html',
                {
                    'carts': cart,
                    'amount': amount,
                    'totalamount': totalamount,
                    'totalitem': totalitem,
                },
            )
        else:
            return render(request, 'app/emptycart.html', {'totalitem': totalitem})
    else:
        # return render(request, 'app/emptycart.html', {'totalitem': totalitem})
        return HttpResponseRedirect('/accounts/login/')
        # pass

# we have 2 options here either we can use empty card rendering with only no_cache decorator , then if the user is not logged in then it shows the empty cart for that user , or we have another option that we can use login_required and never_cache both then automatically if the unautherized user try to access this page he redirect to the login page , in such case the return HttpResponseRedirect('/accounts/login/') is not so important just simply a pass statement is enough because the main function of login_required decorator is to send unauthorized users to the login page if they try to aceess protected route and after successfully login , send to their destination url , but still we use that HttpResponseRedirect('/accounts/login') condition for more better readibilty of code ......

# import thing is that if we not use the login_required decorator and use only pass condtion in the else case and try to access this url for unauthorized user then it will give error that --> views.show_cart didn't return an HttpResponse object. It returned None instead....


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user ==  request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            # print('Quantity', p.quantity)
            # print('Selling Price', p.product.discounted_price)
            # print('Before', amount)
            amount += tempamount
            # print('After', amount)
        # print('Total', amount)
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount,
        }
        return JsonResponse(data)
    else:
        return HttpResponse('')


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            # print('Quantity', p.quantity)
            # print('Selling Price', p.product.discounted_price)
            # print('Before', amount)
            amount += tempamount
            # print('After', amount)
        # print('Total', amount)
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount,
        }
        return JsonResponse(data)
    else:
        return HttpResponse('')


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            # print('Quantity', p.quantity)
            # print('Selling Price', p.product.discounted_price)
            # print('Before', amount)
            amount += tempamount
            # print('After', amount)
        # print('Total', amount)
        data = {'amount': amount, 'totalamount': amount + shipping_amount}
        return JsonResponse(data)
    else:
        return HttpResponse('')

# ________________________________________________________________________________________________________________
# this  are related to payment method.....

import re


@login_required
def checkout(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    user = request.user
    address = Customer.objects.filter(user=user)
    prevpage = request.GET.get('page')
    # print(prevpage)
    cart_items = Cart.objects.filter(user=request.user)
    # print(cart_items)
    flag = True
    totalamount = 0
    shipping_amount = 70.0
    if prevpage.lower() == 'cardpage':
        amount = 0.0
        totalamount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        if cart_product:
            for p in cart_product:
                tempamount = p.quantity * p.product.discounted_price
                amount += tempamount
            totalamount = amount + shipping_amount
    else:
        match = re.search(r'\d+', prevpage)
        if match:
            number = match.group()
            print(number)
            cart_items = Product.objects.filter(id=number)
            if cart_items:
                totalamount = cart_items[0].discounted_price+shipping_amount
                # print(cart_items)
                # print(totalamount)
                flag = False
            else:
                pass

    return render(request, 'app/checkout.html',
                  {'address': address, 'cart_items': cart_items,
                   'totalcost': totalamount, 'totalitem': totalitem, 'flag': flag},
                  )



# when we done payments for some products from our card we have to delete them from cards and save it into order table ...
@login_required
def payment_done(request):
    custid = request.GET.get('custid')
    print('Customer ID', custid)
    user = request.user
    cartid = Cart.objects.filter(user=user)
    customer = Customer.objects.get(id=custid)
    print(customer)
    for cid in cartid:
        OrderPlaced(user=user, customer=customer,
                    product=cid.product, quantity=cid.quantity).save()
        print('Order Saved')
        cid.delete()
        print('Cart Item Deleted')
    return redirect('orders')


# this is the order page of a user here we filter the all orders corresponding to a particular user....
@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    uname = request.user.username
    return render(request, 'app/orders.html', {'order_placed': op, 'uname': uname})

# ___________________________________________________________________________________________________________________________________
# this section is for product list pages.........

# ('M', 'Mobile'),
# ('L', 'Laptop'),
# ('TV', 'Televisions'),
# ('TW', 'Top Wear'),
# ('BW', 'Bottom Wear'),
# ('CM','Cosmetics'),
# ('GR', 'Grocery'),
# ('ST','Stationaries'),
# ('SP','Sports'),


# this is for mobile page where all mobiles will display.....
def mobile(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Redmi' or data == 'Samsung' or data == 'Apple':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(
            category='M').filter(discounted_price__lt=10000)
    elif data == 'above':
        mobiles = Product.objects.filter(
            category='M').filter(discounted_price__gt=10000)
    return render(
        request, 'app/Productpage/mobile.html', {'mobiles': mobiles,
                                                 'totalitem': totalitem}
    )


def grocery(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        grocery = Product.objects.filter(category='GR').order_by('?')
    elif data == 'Veges' or data == 'Fruites' or data == 'Grains' or data == 'snacks':
        grocery = Product.objects.filter(
            category='GR').filter(brand=data).order_by('?')
    elif data == 'above':
        grocery = Product.objects.filter(
            category='GR').filter(discounted_price__gt=1000).order_by('?')
    elif data == 'below':
        grocery = Product.objects.filter(
            category='GR').filter(discounted_price__lt=1000).order_by('?')
    return render(request, 'app/Productpage/Groceys.html', {'grocery': grocery, 'totalitem': totalitem})


def laptop(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        laptop = Product.objects.filter(category='L').order_by('?')
    elif data == 'HP' or data == 'Dell' or data == 'Asus' or data == 'Lenovo':
        laptop = Product.objects.filter(
            category='L').filter(brand=data).order_by('?')
    elif data == 'above':
        laptop = Product.objects.filter(category='L').filter(
            discounted_price__gt=40000).order_by('?')
    elif data == 'below':
        laptop = Product.objects.filter(category='L').filter(
            discounted_price__lt=40000).order_by('?')
    return render(request, 'app/Productpage/laptops.html', {'laptop': laptop, 'totalitem': totalitem})


def tv(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        tv = Product.objects.filter(category='TV').order_by('?')
    elif data == 'Panasonic' or data == 'Sony' or data == 'Samsung':
        tv = Product.objects.filter(category='TV').filter(
            brand=data).order_by('?')
    elif data == 'above':
        tv = Product.objects.filter(
            category='TV').filter(discounted_price__gte=15000).order_by('?')
    elif data == 'below':
        tv = Product.objects.filter(
            category='TV').filter(discounted_price__lte=15000).order_by('?')
    return render(request, 'app/Productpage/television.html', {'tv': tv, 'totalitem': totalitem})


def cosmetic(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        cosmetics = Product.objects.filter(category='CM').order_by('?')
    elif data == 'Perfume' or data == 'Nailpolish' or data == 'lipstick':
        cosmetics = Product.objects.filter(category='CM').filter(
            title__icontains=data).order_by('?')
    elif data == 'above':
        cosmetics = Product.objects.filter(
            category='CM').filter(discounted_price__gte=10000).order_by('?')
    elif data == 'below':
        cosmetics = Product.objects.filter(
            category='CM').filter(discounted_price__lte=10000).order_by('?')

    return render(request, 'app/Productpage/cosmetics.html', {'cosmetics': cosmetics, 'totalitem': totalitem})


def sports(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        sports = Product.objects.filter(category='SP').order_by('?')
    elif data == 'cricket' or data == 'badminton' or data == 'football':
        sports = Product.objects.filter(category='SP').filter(
            title__icontains=data).order_by('?')
    elif data == 'above':
        sports = Product.objects.filter(
            category='SP').filter(discounted_price__gte=10000).order_by('?')
    elif data == 'below':
        sports = Product.objects.filter(
            category='SP').filter(discounted_price__lte=10000).order_by('?')
    return render(request, 'app/Productpage/sports.html', {'sports': sports, 'totalitem': totalitem})


def stationary(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        stationarys = Product.objects.filter(category='ST').order_by('?')
    elif data == 'Copy' or data == 'Drawing' or data == 'books':
        stationarys = Product.objects.filter(category='ST').filter(
            title__icontains=data).order_by('?')
    elif data == 'Classmate':
        stationarys = Product.objects.filter(
            category='ST').filter(brand=data).order_by('?')
    elif data == 'above':
        stationarys = Product.objects.filter(category='ST').filter(
            discounted_price__gte=1000).order_by('?')
    elif data == 'below':
        stationarys = Product.objects.filter(category='ST').filter(
            discounted_price__lte=1000).order_by('?')
    return render(request, 'app/Productpage/stationaries.html', {'stationarys': stationarys, 'totalitem': totalitem})


def topwear(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        topwears = Product.objects.filter(category='TW')
    elif data == 'Safira' or data == 'Bajaj':
        topwears = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'below':
        topwears = Product.objects.filter(category='TW').filter(
            discounted_price__lt=400
        )
    elif data == 'above':
        topwears = Product.objects.filter(category='TW').filter(
            discounted_price__gt=400
        )
    return render(
        request, 'app/Productpage/topwear.html', {'topwears': topwears,
                                                  'totalitem': totalitem}
    )


def bottomwear(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        bottomwears = Product.objects.filter(category='BW')
    elif data == 'Spykar' or data == 'Lee':
        bottomwears = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'below':
        bottomwears = Product.objects.filter(category='BW').filter(
            discounted_price__lt=400
        )
    elif data == 'above':
        bottomwears = Product.objects.filter(category='BW').filter(
            discounted_price__gt=400
        )
    return render(
        request,
        'app/Productpage/bottomwear.html',
        {'bottomwears': bottomwears, 'totalitem': totalitem},
    )

# ________________________________________________________________________________________________________________

# this entire section is for customer registration login and authentication........

# this is for customer registration view.......


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(
                request, 'Congratulations!! Registered Successfully.')
            form.save()
            form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})


# this is for address page.....
# we send this active in the template to add dynamic class in the link of that page we can do the same using the request.path method in the class list in profile page we do this using request.path method in template.....

@login_required
def address(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    add = Customer.objects.filter(user=request.user)
    return render(
        request,
        'app/address.html',
        {'add': add, 'active': 'btn-primary', 'totalitem': totalitem},
    )


# this is for showing the user his profile......

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'totalitem': totalitem})

    def post(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            if (Customer.objects.filter(user=usr, name=name).exists() | Customer.objects.filter(user=usr, locality=locality).exists()):
                messages.warning(
                    request, 'You already have an account with the same username or locality. Please select another!')
                return render(request, 'app/profile.html', {'form': form, 'totalitem': totalitem})
            else:
                reg = Customer(user=usr, name=name, locality=locality,
                               city=city, state=state, zipcode=zipcode)
                reg.save()
                messages.success(
                    request, 'Congratulations!! Profile Updated Successfully.')
                return HttpResponseRedirect('/address/')
        else:
            return render(request, 'app/profile.html', {'form': form, 'totalitem': totalitem})


# all of the pages which are shown after login in that we have to send the totalitem value so that in the cart option user can see how many items he added into carts.....
