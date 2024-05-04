from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from .models import Product, SizeVariant, Category, ProductImage


def Productview(request, slug):
    try:
        product = get_object_or_404(Product, slug=slug)

        color = request.GET.get('color')

        if color is None:
            first_color_image = ProductImage.objects.filter(product=product).first()
            if first_color_image:
                return redirect(f"/products/{slug}/?color={first_color_image.color.color_name}")

        productImages = ProductImage.objects.filter(product=product, color__color_name=color)
        size_variants = SizeVariant.objects.filter(product=product).order_by("size_id")
        color_variants = ProductImage.objects.filter(product=product).values_list('color__color_name', flat=True).distinct()
        sections = Category.objects.values_list('section', flat=True).distinct()
        categories = Category.objects.all()

        context = {'product': product, 'size_variants': size_variants, 'categories': categories, 'sections': sections, 'productImages': productImages, 'color_variants': color_variants}

        return render(request, "products/productview.html", context)

    except Product.DoesNotExist:
        return render(request, "products/error.html")



