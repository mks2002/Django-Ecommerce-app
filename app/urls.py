from django.urls import path
from app import views

# this 2 import is for dealing with media files....
from django.conf import settings
from django.conf.urls.static import static


from django.contrib.auth import views as auth_views

from .forms import (
    LoginForm,
    MyPasswordChangeForm,
    MyPasswordResetForm,
    MySetPasswordForm,
)



urlpatterns = [

    path('', views.ProductView.as_view(), name='home'),

    path(
        'product-detail/<int:pk>/',
        views.ProductDetailView.as_view(),
        name='product-detail',
    ),

    # path('product-detail/<int:pk>/',views.ProductDetailfunc,name='product-detail',),


    # the first url is just for saving the product into the cart table and then it redirect to the 2nd url which will show all the carts product of a particular user ....
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.show_cart, name='showcart'),

    # this 3 are for ajax request to plus minus and remove cart.....
    path('pluscart/', views.plus_cart),
    path('minuscart/', views.minus_cart),
    path('removecart/', views.remove_cart),

    # about us page ...
    path("about/", views.aboutpage, name='about'),

    #  this is for checkout page before doing the payment ...
    path('checkout/', views.checkout, name='checkout'),

    # this is for just saving the data into order table and delete from cart table during payment, payment is done by paypal upi ...
    path('paymentdone/', views.payment_done, name='paymentdone'),

    # direct payment for product without saving it into cart, for single product ...
    path('directpayment/',views.directpayment, name='directpayment'),

    # this is just for displaying all the orders of a particular user ...
    path('orders/', views.orders, name='orders'),


    # this 2 are for showing the adress and profile page to currently logged in user ...
    path('address/', views.address, name='address'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # for updating and deleting the profile ....
    path('profile/update/<id>/', views.update_profile, name='update_profile'),
    path('profile/delete/<id>/', views.delete_profile, name='delete_profile'),


    # from here we started all our product pages ....
    path('grocery/', views.grocery, name='grocery'),
    path('grocery/<slug:data>', views.grocery, name='grocerydata'),

    path('mobile/', views.mobile, name='mobile'),
    path('mobile/<slug:data>', views.mobile, name='mobiledata'),

    path('laptop/', views.laptop, name='laptop'),
    path('laptop/<slug:data>', views.laptop, name='laptopdata'),

    path('tv/', views.tv, name='tv'),
    path('tv/<slug:data>', views.tv, name='tvdata'),

    path('topwear/', views.topwear, name='topwear'),
    path('topwear/<slug:data>', views.topwear, name='topweardata'),

    path('bottomwear/', views.bottomwear, name='bottomwear'),
    path('bottomwear/<slug:data>', views.bottomwear, name='bottomweardata'),

    path('cosmetic/', views.cosmetic, name='cosmetic'),
    path('cosmetic/<slug:data>', views.cosmetic, name='cosmeticdata'),

    path('sport/', views.sports, name='sport'),
    path('sport/<slug:data>', views.sports, name='sportdata'),

    path('stationary/', views.stationary, name='stationary'),
    path('stationary/<slug:data>', views.stationary, name='stationarydata'),



    # for registration we use our custom view class......
    path(
        'registration/',
        views.CustomerRegistrationView.as_view(),
        name='customerregistration',
    ),

    # here we directly use the url for the login view we dont crate any other view for this authentication....
    # if we use the nextpage option directly here in the url then we can override the value of LOGIN_REDIRECT_URL = '/profile/' which is defined in the settings.py file....
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='app/login.html', authentication_form=LoginForm, next_page='home',
        ),
        name='login',
    ),

    # for logout also we dont have to create any view we directly use the built in logout view of django....
    # here we have to pass this nextpage option to say this after logout where it should go otherwise by default it sends to admin logout page....
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),


    # this is password change using old password for this also we dont need to make views we directly use default urls provided by django.......
    path(
        'passwordchange/',
        auth_views.PasswordChangeView.as_view(
            template_name='app/passwordchange.html',
            form_class=MyPasswordChangeForm,
            success_url='/passwordchangedone/',
        ),
        name='passwordchange',
    ),
    # this is also by default url of auth_view we have to modify its properties......
    path(
        'passwordchangedone/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='app/passwordchangedone.html'
        ),
        name='passwordchangedone',
    ),

    # this is for password reset before login here user have to provide his email......
    # this 4 are default urls and default views and the templates are also of the same name just we change the default form by our custom form.....
    # for this 4 we dont have to create any views because here we use the default views we just have to create our custom forms and custom templates......
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='app/password_reset.html', form_class=MyPasswordResetForm
        ),
        name='password_reset',
    ),
    # here user see that a link for password update is send to users email.....
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='app/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    # after clicking on the link user can come to this url where he has to enter the new passwords in the form provided below....
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='app/password_reset_confirm.html',
            form_class=MySetPasswordForm,
        ),
        name='password_reset_confirm',
    ),
    # after user submits the new password he redirect to this url and here he see that password reset successfully....
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='app/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)


# in the password reset url when the form for email come if user enter that email which he use during registration then only the reset password link generate and send to his email if enters any other email then it is not working.....
