from django.urls import path
from products.views import Productview

urlpatterns = [
    path('<slug>/', Productview, name='productview')
]