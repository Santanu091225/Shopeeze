from django.shortcuts import render, get_object_or_404
from .models import Product, SizeVariant, Category


def Productview(request, slug):
    try:
        product = get_object_or_404(Product, slug=slug)

        size_variants = SizeVariant.objects.filter(product=product).order_by("size_id")
        sections = Category.objects.values_list('section', flat=True).distinct()
        categories = Category.objects.all()

        context = {"product": product, "size_variants": size_variants, "categories": categories, "sections": sections}

        return render(request, "products/productview.html", context)

    except Product.DoesNotExist:
        return render(request, "products/product_not_found.html")



