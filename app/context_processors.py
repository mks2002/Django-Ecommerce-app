from .models import Cart


def cart_item_count(request):
    if request.user.is_authenticated:
        total_items = Cart.objects.filter(user=request.user).count()
    else:
        total_items = 0

    return {'total_items_in_cart': total_items}


# this we are making so that we can access this total items in cart in all templates where we want to access it without being pass it through the view function , and also there are some pages like password change and password change done which we acess after login and we render them direcly , without using any view , so to access this value there we have to use this method ...

# after defining this method we have to include it in the settings.py template option ...