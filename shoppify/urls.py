
from django.contrib import admin
from django.urls import path, include


admin.site.site_header = 'Shoppify administration and managment'
admin.site.site_title = 'Shoppify administration and managment'
admin.site.index_title = 'Shoppify administration and managment'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
]
