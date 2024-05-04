from django.db import models
from django.contrib.auth.models import User
from base.models import Basemodel
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import uuid
from products.models import Product, Color, SizeVariant



class Profile(Basemodel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_new_user = models.BooleanField(default=False)
    phone_number = models.PositiveIntegerField()
    is_phone_no_verified = models.BooleanField(default=False)
    otp = models.PositiveIntegerField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='ProfileImages', default='ProfileImages/default_pp.jpg')
    

    def get_cart_count(self):
        return CartItems.objects.filter(cart__user=self.user).count()

    def __str__(self):
        return self.user.first_name



class Address(Basemodel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='adresses')
    receiver = models.CharField(max_length=100)
    mobile = models.IntegerField()
    home = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    district = models.CharField(max_length=100)

    STATE_CHOICES = (
        ("Andhra Pradesh","Andhra Pradesh"),
        ("Arunachal Pradesh ","Arunachal Pradesh "),
        ("Assam","Assam"),
        ("Bihar","Bihar"),
        ("Chhattisgarh","Chhattisgarh"),
        ("Goa","Goa"),
        ("Gujarat","Gujarat"),
        ("Haryana","Haryana"),
        ("Himachal Pradesh","Himachal Pradesh"),
        ("Jammu and Kashmir ","Jammu and Kashmir "),
        ("Jharkhand","Jharkhand"),
        ("Karnataka","Karnataka"),
        ("Kerala","Kerala"),
        ("Madhya Pradesh","Madhya Pradesh"),
        ("Maharashtra","Maharashtra"),
        ("Manipur","Manipur"),
        ("Meghalaya","Meghalaya"),
        ("Mizoram","Mizoram"),
        ("Nagaland","Nagaland"),
        ("Odisha","Odisha"),
        ("Punjab","Punjab"),
        ("Rajasthan","Rajasthan"),
        ("Sikkim","Sikkim"),
        ("Tamil Nadu","Tamil Nadu"),
        ("Telangana","Telangana"),
        ("Tripura","Tripura"),
        ("Uttar Pradesh","Uttar Pradesh"),
        ("Uttarakhand","Uttarakhand"),
        ("West Bengal","West Bengal"),
        ("Andaman and Nicobar Islands","Andaman and Nicobar Islands"),
        ("Chandigarh","Chandigarh"),
        ("Dadra and Nagar Haveli","Dadra and Nagar Haveli"),
        ("Daman and Diu","Daman and Diu"),
        ("Lakshadweep","Lakshadweep"),
        ("National Capital Territory of Delhi","National Capital Territory of Delhi"),
        ("Puducherry","Puducherry"),
    )

    state = models.CharField(choices=STATE_CHOICES,max_length=255)
    landmark = models.CharField(max_length=100, null=True, blank=True)


    def save(self, *args, **kwargs):
        if Address.objects.filter(profile=self.profile).count() >= 5:
            raise ValidationError("A profile can have up to 5 saved addresses.")
        super(Address, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Adresses"


    def __str__(self):
        return f'{self.receiver} - {self.home}, {self.city}, {self.district}, {self.state}, {self.pincode}'


class Cart(Basemodel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Cart')

    def __str__(self):
        return f"{self.user.first_name}'s - cart"


class CartItems(Basemodel):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()

    class Meta:
        verbose_name_plural = "Cart Items"



class Order(Basemodel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(unique=True, max_length=100, editable=False)
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    ORDER_STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Completed", "Completed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Canceled", "Canceled"),
    )
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default="Pending")
    amount = models.PositiveIntegerField(null=True, blank=True)

    rzp_order_id = models.CharField(max_length=100, editable=False, blank=True, null=True)
    rzp_payment_id = models.CharField(max_length=100, editable=False, blank=True, null=True)
    rzp_payment_signature = models.CharField(max_length=100, editable=False, blank=True, null=True)
    PAYMENT_STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Successful", "Successful"),
        ("Failed", "Failed"),
    )
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default="Pending")
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f'ORD{self.uid}'.upper().replace('-', '')[:20]
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Order - {self.user.first_name} {self.user.last_name}"



class OrderItem(Basemodel):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    size = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.order.order_id}"
