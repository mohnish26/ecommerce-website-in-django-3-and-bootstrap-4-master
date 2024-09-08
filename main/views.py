from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Banner, Category, Brand, Product, Image, CartOrder, CartOrderItems, ProductReview, Wishlist, UserAddressBook
from django.db.models import Max, Min, Count, Avg
from django.db.models.functions import ExtractMonth
from django.template.loader import render_to_string
from .forms import SignupForm, ReviewAdd, AddressBookForm, ProfileForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
#paypal
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
import mimetypes
from django.shortcuts import render
from django.db.models import Avg
from .models import Product, Image, ProductReview
from .forms import ReviewAdd
from django import template


# Home Page
def home(request):
	banners=Banner.objects.all().order_by('-id')
	data=Product.objects.filter().order_by('-id')
	return render(request, 'index.html', {'data':data, 'banners':banners})

# Category
def category_list(request):
    data=Category.objects.all().order_by('-id')
    return render(request, 'category_list.html', {'data':data})

# Brand
def brand_list(request):
    data=Brand.objects.all().order_by('-id')
    return render(request, 'brand_list.html', {'data':data})

# Product List
def product_list(request):
	total_data=Product.objects.count()
	data=Product.objects.all().order_by('-id')[:3]
	min_price=Product.objects.aggregate(Min('price'))
	max_price=Product.objects.aggregate(Max('price'))
	return render(request, 'product_list.html', 
		{
			'data':data, 
			'total_data':total_data, 
			'min_price':min_price, 
			'max_price':max_price, 
		}
		)

# Product List According to Category
def category_product_list(request, cat_id):
	category=Category.objects.get(id=cat_id)
	data=Product.objects.filter(category=category).order_by('-id')
	return render(request, 'category_product_list.html', {
			'data':data, 
			})

# Product List According to Brand
def brand_product_list(request, brand_id):
	brand=Brand.objects.get(id=brand_id)
	data=Product.objects.filter(brand=brand).order_by('-id')
	return render(request, 'category_product_list.html', {
			'data':data, 
			})

# Product Detail
def product_detail(request, slug, id):
    product = Product.objects.get(id=id)
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:4]
    reviewForm = ReviewAdd()

    # Check if user can add a review
    canAdd = True
    if request.user.is_authenticated:
        reviewCheck = ProductReview.objects.filter(user=request.user, product=product).count()
        if reviewCheck > 0:
            canAdd = False

    images = Image.objects.filter(product=product)

    # Determine file type for each image
    for image in images:
        # Get all fields of the Image model
        fields = image._meta.fields
        
        # Find the first FileField or ImageField
        file_field = next((f for f in fields if f.get_internal_type() in ['FileField', 'ImageField']), None)
        
        if file_field:
            file_name = getattr(image, file_field.name).name
            mime_type, _ = mimetypes.guess_type(file_name)
            
            if mime_type:
                main_type, sub_type = mime_type.split('/', 1)
                if main_type == 'image':
                    image.file_type = 'image'
                elif main_type == 'video':
                    image.file_type = 'video'
                elif main_type == 'audio':
                    image.file_type = 'audio'
                elif sub_type == 'pdf':
                    image.file_type = 'pdf'
                elif 'wordprocessingml' in sub_type or sub_type == 'msword':
                    image.file_type = 'word'
                elif 'spreadsheetml' in sub_type or sub_type in ['vnd.ms-excel', 'csv']:
                    image.file_type = 'excel'
                elif 'presentationml' in sub_type or sub_type == 'vnd.ms-powerpoint':
                    image.file_type = 'powerpoint'
                else:
                    image.file_type = 'other'
            else:
                # If mimetypes can't determine the type, try to guess from the extension
                ext = file_name.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                    image.file_type = 'image'
                elif ext in ['mp4', 'avi', 'mov', 'wmv']:
                    image.file_type = 'video'
                elif ext in ['mp3', 'wav', 'ogg']:
                    image.file_type = 'audio'
                elif ext == 'pdf':
                    image.file_type = 'pdf'
                elif ext in ['doc', 'docx']:
                    image.file_type = 'word'
                elif ext in ['xls', 'xlsx', 'csv']:
                    image.file_type = 'excel'
                elif ext in ['ppt', 'pptx']:
                    image.file_type = 'powerpoint'
                else:
                    image.file_type = 'other'
        else:
            image.file_type = 'unknown'

    # Fetch reviews
    reviews = ProductReview.objects.filter(product=product)

    # Fetch avg rating for reviews
    avg_reviews = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))

    context = {
        'data': product,
        'images': images,
        'related': related_products,
        'reviewForm': reviewForm,
        'canAdd': canAdd,
        'reviews': reviews,
        'avg_reviews': avg_reviews
    }

    return render(request, 'product_detail.html', context)
	

# Search
def search(request):
	q=request.GET['q']
	data=Product.objects.filter(title__icontains=q).order_by('-id')
	return render(request, 'search.html', {'data':data})

# Filter Data
def filter_data(request):
	colors=request.GET.getlist('color[]')
	categories=request.GET.getlist('category[]')
	brands=request.GET.getlist('brand[]')
	sizes=request.GET.getlist('size[]')
	minPrice=request.GET['minPrice']
	maxPrice=request.GET['maxPrice']
	allProducts=Product.objects.all().order_by('-id').distinct()
	allProducts=allProducts.filter(Product__price__gte=minPrice)
	allProducts=allProducts.filter(Product__price__lte=maxPrice)
	if len(colors)>0:
		allProducts=allProducts.filter(Product__color__id__in=colors).distinct()
	if len(categories)>0:
		allProducts=allProducts.filter(category__id__in=categories).distinct()
	if len(brands)>0:
		allProducts=allProducts.filter(brand__id__in=brands).distinct()
	if len(sizes)>0:
		allProducts=allProducts.filter(Product__size__id__in=sizes).distinct()
	t=render_to_string('ajax/product-list.html', {'data':allProducts})
	return JsonResponse({'data':t})

# Load More
def load_more_data(request):
	offset=int(request.GET['offset'])
	limit=int(request.GET['limit'])
	data=Product.objects.all().order_by('-id')[offset:offset+limit]
	t=render_to_string('ajax/product-list.html', {'data':data})
	return JsonResponse({'data':t}
)

# Add to cart
def add_to_cart(request):
	# del request.session['cartdata']
	cart_p={}
	cart_p[str(request.GET['id'])]={
		'image':request.GET['image'], 
		'title':request.GET['title'], 
		'qty':request.GET['qty'], 
		'price':request.GET['price'], 
	}
	if 'cartdata' in request.session:
		if str(request.GET['id']) in request.session['cartdata']:
			cart_data=request.session['cartdata']
			cart_data[str(request.GET['id'])]['qty']=int(cart_p[str(request.GET['id'])]['qty'])
			cart_data.update(cart_data)
			request.session['cartdata']=cart_data
		else:
			cart_data=request.session['cartdata']
			cart_data.update(cart_p)
			request.session['cartdata']=cart_data
	else:
		request.session['cartdata']=cart_p
	return JsonResponse({'data':request.session['cartdata'], 'totalitems':len(request.session['cartdata'])})

# Cart List Page
def cart_list(request):
	total_amt = 0
	if 'cartdata' in request.session:
		for p_id, item in request.session['cartdata'].items():
			total_amt += int(item['qty'])*float(item['price'])
		return render(request,  'cart.html', {'cart_data':request.session['cartdata'], 'totalitems':len(request.session['cartdata']), 'total_amt':total_amt})
	else:
		return render(request,  'cart.html', {'cart_data':'', 'totalitems':0, 'total_amt':total_amt})

# Delete Cart Item
def delete_cart_item(request):
	p_id=str(request.GET['id'])
	if 'cartdata' in request.session:
		if p_id in request.session['cartdata']:
			cart_data=request.session['cartdata']
			del request.session['cartdata'][p_id]
			request.session['cartdata']=cart_data
	total_amt=0
	for p_id, item in request.session['cartdata'].items():
		total_amt+=int(item['qty'])*float(item['price'])
	t=render_to_string('ajax/cart-list.html', {'cart_data':request.session['cartdata'], 'totalitems':len(request.session['cartdata']), 'total_amt':total_amt})
	return JsonResponse({'data':t, 'totalitems':len(request.session['cartdata'])})

# Delete Cart Item
def update_cart_item(request):
	p_id=str(request.GET['id'])
	p_qty=request.GET['qty']
	if 'cartdata' in request.session:
		if p_id in request.session['cartdata']:
			cart_data=request.session['cartdata']
			cart_data[str(request.GET['id'])]['qty']=p_qty
			request.session['cartdata']=cart_data
	total_amt=0
	for p_id, item in request.session['cartdata'].items():
		total_amt+=int(item['qty'])*float(item['price'])
	t=render_to_string('ajax/cart-list.html', {'cart_data':request.session['cartdata'], 'totalitems':len(request.session['cartdata']), 'total_amt':total_amt})
	return JsonResponse({'data':t, 'totalitems':len(request.session['cartdata'])})

# Signup Form
def signup(request):
	if request.method=='POST':
		form=SignupForm(request.POST)
		if form.is_valid():
			form.save()
			username=form.cleaned_data.get('username')
			pwd=form.cleaned_data.get('password1')
			user=authenticate(username=username, password=pwd)
			login(request,  user)
			return redirect('home')
	form=SignupForm
	return render(request,  'registration/signup.html', {'form':form})


# Checkout
@login_required
def checkout(request):
	total_amt=0
	totalAmt=0
	if 'cartdata' in request.session:
		for p_id, item in request.session['cartdata'].items():
			totalAmt+=int(item['qty'])*float(item['price'])
		# Order
		order=CartOrder.objects.create(
				user=request.user, 
				total_amt=totalAmt
			)
		# End
		for p_id, item in request.session['cartdata'].items():
			total_amt+=int(item['qty'])*float(item['price'])
			# OrderItems
			items=CartOrderItems.objects.create(
				order=order, 
				invoice_no='INV-'+str(order.id), 
				item=item['title'], 
				image=item['image'], 
				qty=item['qty'], 
				price=item['price'], 
				total=float(item['qty'])*float(item['price'])
				)
			# End
		# Process Payment
		host = request.get_host()
		paypal_dict = {
		    'business': settings.PAYPAL_RECEIVER_EMAIL, 
		    'amount': total_amt, 
		    'item_name': 'OrderNo-'+str(order.id), 
		    'invoice': 'INV-'+str(order.id), 
		    'currency_code': 'USD', 
		    'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')), 
		    'return_url': 'http://{}{}'.format(host, reverse('payment_done')), 
		    'cancel_return': 'http://{}{}'.format(host, reverse('payment_cancelled')), 
		}
		form = PayPalPaymentsForm(initial=paypal_dict)
		address=UserAddressBook.objects.filter(user=request.user, status=True).first()
		return render(request,  'checkout.html', {'cart_data':request.session['cartdata'], 'totalitems':len(request.session['cartdata']), 'total_amt':total_amt, 'form':form, 'address':address})

@csrf_exempt
def payment_done(request):
	returnData=request.POST
	return render(request,  'payment-success.html', {'data':returnData})


@csrf_exempt
def payment_canceled(request):
	return render(request,  'payment-fail.html')


# Save Review
def save_review(request, pid):
	product=Product.objects.get(pk=pid)
	user=request.user
	review=ProductReview.objects.create(
		user=user, 
		product=product, 
		review_text=request.POST['review_text'], 
		review_rating=request.POST['review_rating'], 
		)
	data={
		'user':user.username, 
		'review_text':request.POST['review_text'], 
		'review_rating':request.POST['review_rating']
	}

	# Fetch avg rating for reviews
	avg_reviews=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
	# End

	return JsonResponse({'bool':True, 'data':data, 'avg_reviews':avg_reviews})

# User Dashboard
import calendar
def my_dashboard(request):
	orders=CartOrder.objects.annotate(month=ExtractMonth('order_dt')).values('month').annotate(count=Count('id')).values('month', 'count')
	monthNumber=[]
	totalOrders=[]
	for d in orders:
		monthNumber.append(calendar.month_name[d['month']])
		totalOrders.append(d['count'])
	return render(request,  'user/dashboard.html', {'monthNumber':monthNumber, 'totalOrders':totalOrders})

# My Orders
def my_orders(request):
	orders=CartOrder.objects.filter(user=request.user).order_by('-id')
	return render(request,  'user/orders.html', {'orders':orders})

# Order Detail
def my_order_items(request, id):
	order=CartOrder.objects.get(pk=id)
	orderitems=CartOrderItems.objects.filter(order=order).order_by('-id')
	return render(request,  'user/order-items.html', {'orderitems':orderitems})

# Wishlist
@login_required
def add_wishlist(request):
  pid = request.GET.get('product')
  data = {}

  if not pid:
    data['bool'] = False
    return JsonResponse(data, status=400)

  try:
    product = Product.objects.get(pk=pid)
  except Product.DoesNotExist:
    data['bool'] = False
    return JsonResponse(data, status=404)

  checkw = Wishlist.objects.filter(product=product, user=request.user).exists()
  if checkw:
    data['bool'] = False
  else:
    Wishlist.objects.create(product=product, user=request.user)
    data['bool'] = True
  return JsonResponse(data)

# My Wishlist
def my_wishlist(request):
    wlist = Wishlist.objects.filter(user=request.user).order_by('-id')
    wish_list_count = wlist.aggregate(count=Count('id'))['count']
    return render(request, 'user/wishlist.html', {'wlist': wlist, 'wish_list_count': wish_list_count})

@login_required
def delete_wishlist_item(request, product_id):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    wishlist_item.delete()
    return redirect('my_wishlist')

# My Reviews
def my_reviews(request):
	reviews=ProductReview.objects.filter(user=request.user).order_by('-id')
	return render(request,  'user/reviews.html', {'reviews':reviews})

# My AddressBook
def my_addressbook(request):
	addbook=UserAddressBook.objects.filter(user=request.user).order_by('-id')
	return render(request,  'user/addressbook.html', {'addbook':addbook})

# Save addressbook
def save_address(request):
	msg=None
	if request.method=='POST':
		form=AddressBookForm(request.POST)
		if form.is_valid():
			saveForm=form.save(commit=False)
			saveForm.user=request.user
			if 'status' in request.POST:
				UserAddressBook.objects.update(status=False)
			saveForm.save()
			msg='Data has been saved'
	form=AddressBookForm
	return render(request,  'user/add-address.html', {'form':form, 'msg':msg})

# Activate address
def activate_address(request):
	a_id=str(request.GET['id'])
	UserAddressBook.objects.update(status=False)
	UserAddressBook.objects.filter(id=a_id).update(status=True)
	return JsonResponse({'bool':True})

# Edit Profile
def edit_profile(request):
	msg=None
	if request.method=='POST':
		form=ProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			msg='Data has been saved'
	form=ProfileForm(instance=request.user)
	return render(request,  'user/edit-profile.html', {'form':form, 'msg':msg})

# Update addressbook
def update_address(request, id):
	address=UserAddressBook.objects.get(pk=id)
	msg=None
	if request.method=='POST':
		form=AddressBookForm(request.POST, instance=address)
		if form.is_valid():
			saveForm=form.save(commit=False)
			saveForm.user=request.user
			if 'status' in request.POST:
				UserAddressBook.objects.update(status=False)
			saveForm.save()
			msg='Data has been saved'
	form=AddressBookForm(instance=address)
	return render(request,  'user/update-address.html', {'form':form, 'msg':msg})

def upload(request):
    if request.method == 'POST':
        product_data = {
            'name': request.POST.get('name'),
            'slug': request.POST.get('slug'),
            'thumbnail': request.FILES.get('thumbnail'),
            'category': get_object_or_404(Category, id=request.POST.get('category')),
            'brand': get_object_or_404(Brand, id=request.POST.get('brand')),
            'description': request.POST.get('description'),
            'price': request.POST.get('price'),
            'is_featured': request.POST.get('is_featured') == 'on',
            'vendor': request.user
        }
        product = Product.objects.create(**product_data)
        images = request.FILES.getlist('images')
        for image in images:
            Image.objects.create(product=product, images=image)
        messages.success(request, "Product created successfully")
        return redirect("upload")

    categories = Category.objects.all()
    brands = Brand.objects.all()
    context = {
        'categories': categories,
        'brands': brands
    }
    return render(request, "create.html", context)