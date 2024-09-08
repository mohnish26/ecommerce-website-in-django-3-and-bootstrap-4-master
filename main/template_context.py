from .models import Product

def get_filters(request):
	cats=Product.objects.distinct().values('category__title','category__id')
	brands=Product.objects.distinct().values('brand__title','brand__id')
	data={
		'cats':cats,
		'brands':brands,
	}
	return data