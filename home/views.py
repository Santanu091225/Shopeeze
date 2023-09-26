from django.shortcuts import render
from products.models import Product, Category


def index(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    sections = Category.objects.values_list('section', flat=True).distinct()
    context = {'products': products, 'categories': categories, 'sections': sections}
    return render(request, 'home/index.html', context)

