from django.shortcuts import render
from products.models import Product, Category


def index(request):
    products = Product.objects.all()

    limit = 10
    latest_products = products.order_by('created_at')[:limit]
    categories = Category.objects.all()
    sections = Category.objects.values_list('section', flat=True).distinct()
    context = {'products': products, 'categories': categories, 'sections': sections, 'latest_products': latest_products}
    return render(request, 'home/index.html', context) 

