from django.db import models
from django.utils.html import mark_safe
from django.contrib.auth.models import User


# Banner
class Banner(models.Model):
    img = models.ImageField(upload_to="banner_imgs/")
    alt_text = models.CharField(max_length=300)

    class Meta:
        verbose_name_plural = '1. Banners'

    def image_tag(self):
        return mark_safe('<img src = "%s" width = "100" />' % (self.img.url))

    def __str__(self):
        return self.alt_text


# Category
class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="cat_imgs/")

    class Meta:
        verbose_name_plural = '2. Categories'

    def image_tag(self):
        return mark_safe('<img src = "%s" width = "50" height = "50" />' % (self.image.url))

    def __str__(self):
        return self.title


# Brand
class Brand(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="brand_imgs/")

    class Meta:
        verbose_name_plural = '3. Brands'

    def __str__(self):
        return self.title


# Product Model
class Product(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=400)
    thumbnail = models.ImageField(upload_to="product_imgs/", null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.IntegerField()
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = '4. Products'

    def __str__(self):
        return self.name


# Product Image
class Image(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    images = models.ImageField(upload_to="img")

    class Meta:
        verbose_name_plural = '5. ProductImages'

    def __str__(self):
        return self.product.name

    def image_tag(self):
        return mark_safe('<img src = "%s" width = "50" height = "50" />' % (self.image.url))


# Order
status_choice = (
        ('process', 'In Process'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )


class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amt = models.FloatField()
    paid_status = models.BooleanField(default=False)
    order_dt = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(choices=status_choice, default='process', max_length=150)

    class Meta:
        verbose_name_plural = '6. Orders'


# OrderItems
class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=150)
    item = models.CharField(max_length=150)
    thumbnail = models.CharField(max_length=200)
    qty = models.IntegerField()
    price = models.FloatField()
    total = models.FloatField()

    class Meta:
        verbose_name_plural = '7. Order Items'

    def image_tag(self):
        return mark_safe('<img src = "/media/%s" width = "50" height = "50" />' % (self.image))


# Product Review
RATING = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review_text = models.TextField()
    review_rating = models.CharField(choices=RATING, max_length=150)

    class Meta:
        verbose_name_plural = 'Reviews'

    def get_review_rating(self):
        return self.review_rating


# WishList
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Wishlist'


# AddressBook
class UserAddressBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=50, null=True)
    address = models.TextField()
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'AddressBook'

