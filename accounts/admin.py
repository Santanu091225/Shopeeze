from django.contrib import admin
from .models import *


admin.site.register(Profile)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address_with_user', 'city', 'state', 'pincode')

    def address_with_user(self, obj):
        # Get the count of addresses up to the current address
        count = Address.objects.filter(profile=obj.profile, uid__lte=obj.uid).count()
        return f"Address {count} - {obj.profile.user.first_name}"
    address_with_user.short_description = 'Address'


admin.site.register(Cart)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('order_id', 'rzp_order_id', 'rzp_payment_id', 'rzp_payment_signature')
    list_display = ('order_with_user', 'order_id', 'amount', 'order_status', 'payment_status')
    model = Order

    def order_with_user(self, obj):
        count = Order.objects.filter(user=obj.user, uid__lte=obj.uid).count()
        return f"Order {count} - {obj.user.first_name}"


@admin.register(CartItems)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'quantity']
    model = CartItems


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'size', 'color', 'quantity']
    model = OrderItem


