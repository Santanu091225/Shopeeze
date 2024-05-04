from django.db import models
from base.models import Basemodel
from django.utils.text import slugify


class Category(Basemodel):
    SECTION_CHOICES = (
        ('Men', 'Men'),
        ('Women', 'Women'),
    )
    section = models.CharField(max_length=10, choices=SECTION_CHOICES, default='')
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null= True, blank=True)
    category_image = models.ImageField(upload_to='categories')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.section}'s {self.category_name}"

    class Meta:
        verbose_name_plural = "Categories"

class Brand(Basemodel):
    brand_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.brand_name

class Fabric(Basemodel):
    fabric_name = models.CharField(max_length=100)

    def __str__(self):
        return self.fabric_name


class SizeVariant(Basemodel):
    size_name = models.CharField(max_length=100)
    size_id = models.IntegerField(unique=True)
    def __str__(self):
        return self.size_name


class Color(Basemodel):
    color_name = models.CharField(max_length=100)


    def __str__(self):
        return self.color_name


class Product(Basemodel):
    product_name = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, null=True, blank=True, editable=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="product_brand")
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE, related_name="fabric", default='Unknown')
    size_variant = models.ManyToManyField(SizeVariant)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="product_category")
    actual_price = models.IntegerField()
    discount_percentage = models.IntegerField(null=True, blank=True, editable=False)
    discount_price = models.IntegerField(null=True, blank=True)
    product_description = models.TextField()
    

    def __str__(self):
        return self.product_name


    def save(self, *args, **kwargs):
        if self.discount_price:
            self.discount_percentage = int(((self.actual_price - self.discount_price) / self.actual_price) * 100)
        else:
            self.discount_percentage = None

        # Ensure discount_percentage is within the valid range
        if self.discount_percentage is not None:
            self.discount_percentage = max(0, min(99, self.discount_percentage))

        # Generate the slug from the product name
        self.slug = slugify(self.product_name)

        super(Product, self).save(*args, **kwargs)


class ProductImage(Basemodel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    product_image = models.ImageField(upload_to='products')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="color")

    def __str__(self):
          return f"{self.product.product_name} - {self.color.color_name} Image"



