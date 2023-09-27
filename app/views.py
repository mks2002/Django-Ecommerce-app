import re
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages

from django.contrib.auth.models import User
from .models import Customer, Product, Cart, OrderPlaced, Comment
from .forms import CustomerRegistrationForm, CustomerProfileForm, CommentForm

from django.views import View
from django.views.decorators.cache import never_cache

from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# it is for showing all the products in the testinomials in the main page .....

from django.db.models import OuterRef, Subquery

# this 2 is used for redirecting into checkout from profile page ...
from urllib.parse import urlencode
from django.urls import reverse

# this is for getting current timestamp ....
from django.utils import timezone


# this is for sending activation email during signup ....
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .utils import TokenGenerator, generate_token
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings

# this we have to import for using linebreak in the message which we pass in the templates ....
from django.utils.safestring import mark_safe

# this are related to custom login view function ......
from django.contrib.auth import authenticate, login
from .forms import LoginForm


@method_decorator(never_cache, name='dispatch')
class ProductView(View):
    def get(self, request):
        totalitem = 0
        topwears = Product.objects.filter(category='TW').order_by('?')
        bottomwears = Product.objects.filter(category='BW').order_by('?')
        grocery = Product.objects.filter(category='GR').order_by('?')

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


'''
# here we have to use same code in both get and post method , so we try to keep all common codes at one place in modified method ..

@method_decorator(never_cache, name='dispatch')
class ProductDetailView(View):

    def get(self, request, pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        print(product.id)
        fm = CommentForm()
        comments=Comment.objects.filter(product=product).order_by('-timestamp')
        # if there are more then 5 comments then we only show the most new 5 comments ..
        if len(comments)>5:
            comments=comments[:5]
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)).exists()
            # only if the user is authenticated then show this message..
            messages.info(request,'here you can add your comment !')

        return render(
            request,
            'app/productdetail.html',
            {
                'product': product,
                'forms': fm,
                'item_already_in_cart': item_already_in_cart,
                'comments':comments,
                'totalitem': totalitem,
            },
        )

    def post(self, request, pk):
        totalitem = 0
        form = CommentForm(request.POST)
        item_already_in_cart = False
        product = Product.objects.get(id=pk)
        comments=Comment.objects.filter(product=product).order_by('-timestamp')
        if len(comments)>5:
            comments=comments[:5]
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)).exists()

        if form.is_valid():
            usr = request.user
            comment = form.cleaned_data['description']
            timestamp = timezone.now()
            # both the if statements doing the same work .....
            # if OrderPlaced.objects.filter(product=product,user=request.user).exists():
            if OrderPlaced.objects.filter(Q(product=product) & Q(user=request.user)).exists():
                if Comment.objects.filter(user=usr, product=product, description=comment).exists():
                    messages.warning(request,'You already made this same comment before!')
                else:
                    result = Comment(user=usr, product=product, description=comment, timestamp=timestamp)
                    result.save()
                    form = CommentForm()
                    messages.success(request, 'Your comment is added successfully !')
            else:
                messages.warning(request,'First you need to purchase this product to make a comment !!')
        else :
            # messages.error(request,'something error occured !!')
            pass
        return render(request, 'app/productdetail.html', {
                'product': product,
                'forms': form,
                'item_already_in_cart': item_already_in_cart,
                 'comments':comments,
                'totalitem': totalitem,
            },)
'''

# for filtering we can use product.id but when we have to save it into the database then we need to pass the entire product value ...

# In Django, if you use the login_required decorator above a view function and a user tries to access that view without being logged in, Django will automatically redirect the user to the login page....

# here code repeatation is less and also we use the functionalities of python object oriented programming.....


@method_decorator(never_cache, name='dispatch')
class ProductDetailView(View):
    template_name = 'app/productdetail.html'
    comment_form_class = CommentForm

    def __init__(self):
        super().__init__()
        self.pk = None

    def get_common_data(self, request, product):
        totalitem = 0
        comments = Comment.objects.filter( product=product).order_by('-timestamp')
        # if there are more then 5 comments then we only show the most new 5 comments ....
        if len(comments) > 5:
            comments = comments[:5]
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            # if exists then it is true else false ...
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)).exists()
        return totalitem, comments, item_already_in_cart

    def get(self, request, pk):
        self.pk = pk  # Set the pk as an instance attribute
        product = Product.objects.get(pk=self.pk)
        totalitem, comments, item_already_in_cart = self.get_common_data(
            request, product)
        fm = self.comment_form_class()
        if request.user.is_authenticated:
            messages.info(request, 'here you can add your comment !')
        return render(
            request,
            self.template_name,
            {
                'product': product,
                'forms': fm,
                'item_already_in_cart': item_already_in_cart,
                'comments': comments,
                'totalitem': totalitem,
            },
        )

    def post(self, request, pk):
        self.pk = pk
        product = Product.objects.get(id=self.pk)
        totalitem, comments, item_already_in_cart = self.get_common_data(
            request, product)
        form = self.comment_form_class(request.POST)

        if form.is_valid():
            usr = request.user
            comment = form.cleaned_data['description']
            timestamp = timezone.now()
            # both the if statements doing the same work .....
            # if OrderPlaced.objects.filter(product=product,user=request.user).exists():
            if OrderPlaced.objects.filter(Q(product=product) & Q(user=usr)).exists():
                if Comment.objects.filter(user=usr, product=product, description=comment).exists():
                    messages.warning( request, 'You already made this same comment before!')
                else:
                    result = Comment(user=usr, product=product, description=comment, timestamp=timestamp)
                    result.save()
                    form = self.comment_form_class()
                    messages.success( request, 'Your comment is added successfully!')
                    # so that the values are updated afer the form is submiting ...
                    totalitem, comments, item_already_in_cart = self.get_common_data(
                        request, product)
            else:
                # if this product is not purchased by that user then he cant make comment ...-
                messages.warning( request, 'You need to purchase this product to make a comment!')
        else:
            # messages.error(request, 'Something error occurred!')
            pass

        return render(request, self.template_name, {
            'product': product,
            'forms': form,
            'item_already_in_cart': item_already_in_cart,
            'comments': comments,
            'totalitem': totalitem,
        },)


# about us page ...
@never_cache
def aboutpage(request):
    return render(request, 'app/Aboutpage.html')

# ________________________________________________________________________________________________________

# this section is related to cart options and multiple operations on carts ....


# in the add to cart we use login_required decorator so that if somebody not logged in then he cant able to acess this page and cant able to add Product in the cart....
@login_required()
def add_to_cart(request):
    user = request.user
    item_already_in_cart1 = False
    product_id = request.GET.get('prod_id')
    # if item already in cart then it become true.....
    item_already_in_cart1 = Cart.objects.filter(
        Q(product=product_id) & Q(user=request.user)).exists()
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
        # print(cart)
        prodamount = 0.0
        shipping_amount = 70.0
        # this will cnt the number of different product in the cart so that we add delivery charge on each different product ...
        prodcnt = 0
        totalamount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        # print(cart_product)

        # shipping amount we directly add in the template ...
        if cart_product:
            for p in cart_product:
                tempamount = p.quantity * p.product.discounted_price
                prodamount += tempamount
                prodcnt += 1
                # amount+=shipping_amount

            amount = prodamount
            totalamount = amount + (70*prodcnt)

            return render(
                request,
                'app/addtocart.html',
                {
                    'carts': cart,
                    'prodcnt': prodcnt,
                    'amount': amount,
                    'totalitem': totalitem,
                    'totalamount': totalamount
                },
            )
        else:
            return render(request, 'app/emptycart.html', {'totalitem': totalitem})
    else:
        # return render(request, 'app/emptycart.html', {'totalitem': totalitem})
        return HttpResponseRedirect('/accounts/login/')
        # pass

# we can iterate on queryset as well as on lists both , so we can use any 1 of those here for iterating we use list method ,but if we want we can direcly iterate on the queryset also ...

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
        prodcnt = 0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            # print('Quantity', p.quantity)
            # print('Selling Price', p.product.discounted_price)
            # print('Before', amount)
            amount += tempamount
            prodcnt += 1
            # print('After', amount)
        # print('Total', amount)
        totalamount = amount + (shipping_amount*prodcnt)
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'prodcnt': prodcnt,
            'totalamount': totalamount,
        }
        return JsonResponse(data)
    else:
        return HttpResponse('')


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))

        # user cant reduce the quantity less then 1 ..
        if c.quantity > 1:
            c.quantity -= 1
        else:
            pass
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        prodcnt = 0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            # print('Quantity', p.quantity)
            # print('Selling Price', p.product.discounted_price)
            # print('Before', amount)
            amount += tempamount
            prodcnt += 1
            # print('After', amount)
        # print('Total', amount)
        totalamount = amount + (shipping_amount*prodcnt)
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'prodcnt': prodcnt,
            'totalamount': totalamount,
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
        prodcnt = 0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            # print('Quantity', p.quantity)
            # print('Selling Price', p.product.discounted_price)
            # print('Before', amount)
            amount += tempamount
            prodcnt += 1
            # print('After', amount)
        # print('Total', amount)
        totalamount = amount + (shipping_amount*prodcnt)
        msg = 'Product removed from cart successfully !!'
        if totalamount == 0:
            msg = 'Your cart is now empty !! '
        data = {
            'amount': amount,
            'prodcnt': prodcnt,
            'totalamount': totalamount,
            'msg': msg,
        }
        return JsonResponse(data)
    else:
        return HttpResponse('')

# ______________________________________________________________________________________________________________

# this  are related to payment method.....


@login_required
@never_cache
def checkout(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    user = request.user
    address = Customer.objects.filter(user=user)
    addresscnt = address.count()
    print(addresscnt)

    prevpage = request.GET.get('page')
    # print(prevpage)
    cart_items = Cart.objects.filter(user=request.user)
    # print(cart_items)
    flag = True
    totalamount = 0
    shipping_amount = 70.0
    Prodcnt = 0  # it count differents type of product ..
    number = 0
    if prevpage.lower() == 'cardpage':
        amount = 0.0
        totalamount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        if cart_product:
            for p in cart_product:
                tempamount = p.quantity * p.product.discounted_price
                amount += tempamount
                Prodcnt += 1
            totalamount = amount + (shipping_amount * Prodcnt)
    else:
        Prodcnt = 1
        match = re.search(r'\d+', prevpage)
        if match:
            number = match.group()
            # print(number)
            cart_items = Product.objects.filter(id=number)
            if cart_items:
                totalamount = cart_items[0].discounted_price+shipping_amount
                # print(cart_items)
                # print(totalamount)
                flag = False
            else:
                pass

    return render(request, 'app/checkout.html',
                  {'address': address,
                   'cart_items': cart_items,
                   'totalcost': totalamount,
                   'totalitem': totalitem,
                   'flag': flag, 'number': number,
                   'addresscnt': addresscnt, 'prodcnt': Prodcnt,
                   'prevpage': prevpage},
                  )
# we use this addresscnt variable so that if it is 0 then we have to prevent to show the payment button , and user need to first complete his profile by adding address then we show the payment option to him ....

# we use a flag variable in template for different kind of payments for direct payment I use flag=false, and for payment of cart items we use flag=true......

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
    messages.success(request, 'Your order is placed successfully !')
    return redirect('orders')


# this is for direct payment without saving into the cart...
@login_required
def directpayment(request):
    custid = request.GET.get('custid')
    prodid = request.GET.get('productid')
    product = Product.objects.get(id=prodid)
    user = request.user
    customer = Customer.objects.get(id=custid)
    result = OrderPlaced(user=user, customer=customer,
                         product=product, quantity=1)
    result.save()
    messages.success(request, 'Your order is placed successfully !')
    return redirect('orders')


# this is the order page of a user here we filter the all orders corresponding to a particular user....
@login_required
def orders(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    op = OrderPlaced.objects.filter(user=request.user)
    uname = request.user.username
    return render(request, 'app/orders.html', {'order_placed': op,  'uname': uname, 'totalitem': totalitem})


# _________________________________________________________________________________________________________

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
        if not request.user.is_authenticated:
            form = CustomerRegistrationForm()
            return render(request, 'app/customerregistration.html', {'form': form})
        else:
            messages.warning(
                request, 'You are already logged in so you cant access this page !')
            return HttpResponseRedirect('/')

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.warning(
                    request, 'this email is already used, select another !')
            else:
                messages.success(request, mark_safe(
                    'Congratulations!! Registered Successfully.<br/>An email is sent to your account for activation .'))
                # Create a user instance but don't save it to the database yet.
                user = form.save(commit=False)
                # Set the is_active attribute to False.
                user.is_active = False
                # Save the user with is_active set to False.
                user.save()
                form = CustomerRegistrationForm()
                email_subject = 'Activate your account !!'
                message = render_to_string('app/activate.html', {
                    'user': user,
                    'domain': '127.0.0.1:8000',
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': generate_token.make_token(user),
                })
                email_message = EmailMessage(
                    email_subject, message, settings.EMAIL_HOST_USER, [email])
                email_message.send()
        return render(request, 'app/customerregistration.html', {'form': form})


# this is for activating the account ...
class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as identifier:
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.info(request, mark_safe(
                'Account Activated Successfully !!<br/>Now you can login into your account . '))
            return redirect('/accounts/login/')
        return render(request, 'app/activatefail.html')

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


# this is related to user profile page and update the profile ....
# this is for showing the user his profile......


@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class ProfileView(View):
    def get(self, request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        form = CustomerProfileForm()
        messages.info(request, 'Here you can add your different address !')
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
                messages.error(
                    request, 'You already have an account with the same username or locality. Please select another!')
                return render(request, 'app/profile.html', {'form': form, 'totalitem': totalitem})
            else:
                reg = Customer(user=usr, name=name, locality=locality,
                               city=city, state=state, zipcode=zipcode)
                reg.save()
                prevdest = request.GET.get('prevpage', None)

                if prevdest == 'checkout':
                    # this is how we have to generate the redirect url with get parameter ..
                    page = request.GET.get('page', None)
                    query_params = urlencode({'page': page}) if page else ''
                    redirect_url = reverse('checkout') + f'?{query_params}'
                    # print(redirect_url)
                    messages.success(
                        request, 'Congratulations!! your profile created Successfully.')
                    return HttpResponseRedirect(redirect_url)
                else:
                    messages.success(
                        request, 'Congratulations!! your profile created Successfully.')
                    return HttpResponseRedirect('/address/')
        else:
            return render(request, 'app/profile.html', {'form': form, 'totalitem': totalitem})


# all of the pages which are shown after login in that we have to send the totalitem value so that in the cart option user can see how many items he added into carts.....

# for updating and deleting we create our custom functions ....

@login_required()
def update_profile(request, id):
    print(type(id))
    id = int(id)
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    customer = Customer.objects.filter(user=request.user, id=id)[0]

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your profile is updated successfully ! ')
            return HttpResponseRedirect('/address/')
        else:
            messages.error(request, 'Some error occurs !')
            return render(request, 'app/profile.html', {'form': form, 'totalitem': totalitem})

    if request.method == 'GET':
        form = CustomerProfileForm(instance=customer)
        messages.warning(
            request, 'Here you can update your existing profile !')
        return render(request, 'app/profile.html', {'form': form, 'totalitem': totalitem})

# by default all the values which extracted from the url is in form of string so for safety we have to first convert it into integer then do our further work ...


'''

@login_required
def delete_profile(request, id):
    # if we want we can use directly get method because there is only one customer which satisfy this condition ....
    customer = Customer.objects.filter(user=request.user, id=id)[0]
    OrderPlaced.objects.filter(user=request.user, customer=customer).delete
    Customer.objects.filter(user=request.user, id=id).delete()
    messages.warning(request, 'Your Profile is deleted succesfully ! ')
    return HttpResponseRedirect('/address/')

'''

# modified version of delete profile for user ....
# if a Customer has active order which is associated with its profile then that profile cant be deleted untill the order deliverd or cancelled ...


@login_required
def delete_profile(request, id):
    customer = Customer.objects.filter(user=request.user, id=id).first()

    if customer:
        active_orders = OrderPlaced.objects.filter(
            user=request.user, customer=customer).exclude(status__in=['Delivered', 'Cancel'])

        if active_orders.exists():
            messages.error(
                request, 'You have active orders associated with this profile, So this Profile cannot be deleted !!')
            return HttpResponseRedirect('/address/')
        else:
            OrderPlaced.objects.filter(
                user=request.user, customer=customer).delete()
            customer.delete()
            messages.warning(request, 'Your Profile is deleted successfully!')
            return HttpResponseRedirect('/address/')
    else:
        messages.error(request, 'Profile not found.')
        return HttpResponseRedirect('/address/')
