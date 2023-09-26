from django.contrib import admin
from .models import *


admin.site.register(Category)

admin.site.register(Brand)
admin.site.register(Fabric)

class ProductImageAdmin(admin.StackedInline):
    model = Product_image

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'actual_price', 'discount_price', 'discount_percentage', 'category', 'slug', 'brand', 'fabric',)
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:
            readonly_fields.extend(['discount_percentage', 'slug'])
        return readonly_fields
    inlines = [ProductImageAdmin]


admin.site.register(ColorVariant)


@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ['size_name']
    ordering = ['size_id']
    model = SizeVariant


admin.site.register(Product, ProductAdmin)

admin.site.register(Product_image)
