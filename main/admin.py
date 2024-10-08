from django.contrib import admin
from .models import Banner, Category, Brand, Product, Image, CartOrder, CartOrderItems, ProductReview, Wishlist, UserAddressBook

# admin.site.register(Banner)
admin.site.register(Brand)

class BannerAdmin(admin.ModelAdmin):
    list_display=('alt_text', 'image_tag')
admin.site.register(Banner, BannerAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display=('title', 'image_tag')
admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'thumbnail', 'category', 'brand', 'is_featured')
    list_editable = ['is_featured']  # Use square brackets for a list

admin.site.register(Product, ProductAdmin)

# Product Attribute
class ImageAdmin(admin.ModelAdmin):
    list_display=('id', 'images')
admin.site.register(Image, ImageAdmin)

# Order
class CartOrderAdmin(admin.ModelAdmin):
    list_editable=('paid_status', 'order_status')
    list_display=('user', 'total_amt', 'paid_status', 'order_dt', 'order_status')
admin.site.register(CartOrder, CartOrderAdmin)

class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display=('invoice_no', 'item', 'thumbnail', 'qty', 'price', 'total')
admin.site.register(CartOrderItems, CartOrderItemsAdmin)

class ProductReviewAdmin(admin.ModelAdmin):
    list_display=('user', 'product', 'review_text', 'get_review_rating')
admin.site.register(ProductReview, ProductReviewAdmin)

admin.site.register(Wishlist)

class UserAddressBookAdmin(admin.ModelAdmin):
    list_display=('user', 'address', 'status')
admin.site.register(UserAddressBook, UserAddressBookAdmin)


