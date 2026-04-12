from rest_framework import serializers
from base import models
from django.utils.translation import gettext_lazy as _

class GetAllProductListSerializer(serializers.ModelSerializer):
    # We will calculate these in the View using SQL annotations for speed
    lowest_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    highest_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    categories = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = [
            'id', 
            'name', 
            'categories', 
            'lowest_price', # e.g., "From $10.00"
            'highest_price',
            'average_rating', 
            'review_count',
            'thumbnail', 
            'created_at',
            'is_active',
            'is_bestseller'
        ]

    def get_thumbnail(self, obj):
        # 1. Look for an explicitly marked thumbnail across all pre-fetched variants
        for variant in obj.variants.all():
            for image in variant.images.all():
                if image.is_thumbnail and image.img:
                    return image.img.url
                    
        # 2. Fallback: if no thumbnail is set, just return the first available image
        for variant in obj.variants.all():
            for image in variant.images.all():
                if image.img:
                    return image.img.url
                    
        return None  # Return placeholder URL if needed

    def get_categories(self, obj):
        return [cat.name for cat in obj.categories.all()]


class VariantSerializer(serializers.ModelSerializer):
    # Flatten the image URL list for the frontend
    images = serializers.SerializerMethodField()
    product_name = serializers.CharField(source="product.name", read_only=True)
    categories = serializers.SerializerMethodField()
    class Meta:
        model = models.ProductVariant
        fields = ['id','product_name','categories', 'volume', 'price', 
                  'compare_at_price', 'stock', 'images', 'is_on_sale','is_active']

    def get_images(self, obj):
        # Returns a list of dictionaries: [{"id": 1, "url": "cloud/img1.jpg"}, ...]
        return [{"id": img.id, "url": img.img.url,"is_thumbnail":img.is_thumbnail} for img in obj.images.all() if img.img]

    def get_categories(self, obj):
        return [cat.name for cat in obj.product.categories.all()]

class ProductDetailSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True, read_only=True)
    
    categories = serializers.SerializerMethodField()
    
    # Aggregate data for the main header
    rating = serializers.FloatField(source='average_rating_value', read_only=True)

    class Meta:
        model = models.Product
        fields = [
            'id', 'name', 'description', 'categories', 'fragrance_family', 'concentration', 
            'variants', 'rating', 'created_at','is_active', 'is_bestseller'
        ]

    def get_categories(self, obj):
        return [cat.name for cat in obj.categories.all()]

class DashboardProductDetailSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True, read_only=True)
    categories = serializers.SerializerMethodField()
    rating = serializers.FloatField(source='average_rating_value', read_only=True)

    class Meta:
        model = models.Product
        fields = [
            'id', 'name', 'name_en', 'name_ar', 
            'description', 'description_en', 'description_ar', 
            'categories', 
            'fragrance_family', 'fragrance_family_en', 'fragrance_family_ar', 
            'concentration', 'concentration_en', 'concentration_ar', 
            'variants', 'rating', 'created_at', 'is_active', 'is_bestseller'
        ]

    def get_categories(self, obj):
        return [cat.name for cat in obj.categories.all()]

class CartItemSerializer(serializers.ModelSerializer):
    # We use the VariantSerializer to show full details (size, color, image)
    product_id = serializers.CharField(source='variant.product.id')
    variant = VariantSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = models.CartItem
        fields = ['id', 'variant','product_id', 'quantity', 'price', 'subtotal']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = models.Cart
        fields = ['id', 'items', 'total_price', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'name', 'name_en', 'name_ar'] 

    def create(self, validated_data):
        if not validated_data.get('name_ar'):
            validated_data['name_ar'] = validated_data.get('name_en', '')
        return super().create(validated_data)

class GovernorateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Governorate
        fields = ['id', 'name', 'shipping_fee']

class DashboardGovernorateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Governorate
        fields = ['id', 'name_en', 'name_ar', 'shipping_fee', 'is_active']

    def create(self, validated_data):
        if not validated_data.get('name_ar'):
            validated_data['name_ar'] = validated_data.get('name_en', '')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('name_en') and not validated_data.get('name_ar'):
            validated_data['name_ar'] = validated_data['name_en']
        return super().update(instance, validated_data)

class DashboardCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'name_en', 'name_ar', 'is_active']

    def create(self, validated_data):
        if not validated_data.get('name_ar'):
            validated_data['name_ar'] = validated_data.get('name_en', '')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('name_en') and not validated_data.get('name_ar'):
            validated_data['name_ar'] = validated_data['name_en']
        return super().update(instance, validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(source='variant.product.name', read_only=True)
    variant_volume = serializers.CharField(source='variant.volume', read_only=True)
    
    class Meta:
        model = models.OrderItem
        fields = ['variant_name','variant_volume', 'quantity', 'price', 'subtotal','created_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    governorate_name = serializers.CharField(source='governorate.name', read_only=True)
    
    class Meta:
        model = models.Order
        fields = ['id', 'status', 'total_price', 'created_at', 'items', 
                  'full_name', 'full_address', 'phone_number', 'country', 'guest_email',
                  'shipping_fee', 'governorate_name']
        read_only_fields = ['id', 'status', 'total_price', 'created_at', 'items', 'shipping_fee', 'governorate_name']

class CreateOrderSerializer(serializers.ModelSerializer):
    governorate_id = serializers.IntegerField(write_only=True, required=True, help_text="ID of the shipping Governorate")
    class Meta:
        model = models.Order
        fields = ['full_name', 'full_address', 'phone_number', 'country', 'order_notes', 'governorate_id', 'guest_email']

class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model = models.Review
        fields = ['id', 'customer_name', 'rating', 'comment', 'created_at']

class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ['product', 'rating', 'comment']

    def validate(self, data):
        request = self.context.get('request')

        # 1. Check the user hasn't already reviewed this product
        if models.Review.objects.filter(customer=request.user, product=data['product']).exists():
            raise serializers.ValidationError(_("You have already reviewed this product."))

        # 2. Check the user has a DELIVERED order containing this product
        has_purchased = models.OrderItem.objects.filter(
            order__customer=request.user,
            order__status='delivered',
            variant__product=data['product']
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError(_("You can only review products you have purchased and received."))

        return data

class WishlistSerializer(serializers.ModelSerializer):
    # We reuse the list serializer so the wishlist looks just like the shop page
    products = GetAllProductListSerializer(many=True, read_only=True)

    class Meta:
        model = models.WishList
        fields = ['products']

# DASHBOARD SERIALIZERS
class DashBoardOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['status']

    def validate_status(self, value):
        # 1. Check valid choices
        valid_statuses = ["cancelled", "delivered", "shipped", "paid", "pending", "awaiting_payment", "refunded"]
        if value not in valid_statuses:
            raise serializers.ValidationError(_("Invalid status choice."))
        
        # 2. Check logic (e.g., can't manually set to paid)
        if value == 'paid':
             raise serializers.ValidationError(_("You cannot manually mark an order as Paid."))

        # 3. Refund only allowed for paid/shipped/delivered orders
        if value == 'refunded':
            current_status = self.instance.status if self.instance else None
            if current_status not in ['paid', 'shipped', 'delivered']:
                raise serializers.ValidationError(_("You can only refund orders that are Paid, Shipped, or Delivered."))
             
        return value

class DashBoardLowProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id', 'name', 'stock'] # Ensure your Product model has a 'stock' field (or it might be on the Variant)

class DashBoardTopSalesSerializer(serializers.ModelSerializer):
    sales = serializers.IntegerField(read_only=True) # This field comes from the .annotate() in the view

    class Meta:
        model = models.Product
        fields = ['id', 'name', 'sales']
    
class DashBoardOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment_method = serializers.SerializerMethodField()
    governorate_name_en = serializers.CharField(source='governorate.name_en', read_only=True)
    governorate_name_ar = serializers.CharField(source='governorate.name_ar', read_only=True)
    
    class Meta:
        model = models.Order
        fields = ['id', 'status', 'total_price', 'created_at', 'items', 
                  'full_name', 'full_address', 'phone_number', 'country', 'guest_email', 'payment_method',
                  'shipping_fee', 'governorate_name_en', 'governorate_name_ar']
        read_only_fields = ['id', 'status', 'total_price', 'created_at', 'items', 'shipping_fee']

    def get_payment_method(self, obj):
        # Payment is a OneToOneField with related_name='payment'
        payment = getattr(obj, 'payment', None)
        if payment:
            return payment.method
        return None

class DashBoardReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = models.Review
        fields = ['id', 'customer_name','product_name', 'rating', 'comment', 'created_at']

#####################


# serializers.py

# 1. Image Upload Serializer (Simple)
class DashboardVariantImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductImage
        fields = ['id','img']

class DashboardVariantListSerializer(serializers.ListSerializer):
    def validate(self, attrs):
        # Check for duplicate volumes in the incoming bulk request
        volumes = [item.get('volume') for item in attrs if item.get('volume')]
        if len(volumes) != len(set(volumes)):
            raise serializers.ValidationError(_("Duplicate volumes are not allowed in the same request."))
        return super().validate(attrs)



# 2. Create Variant Serializer (No Images here, just data)
class DashboardVariantCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = models.ProductVariant
        # We ONLY include fields that the user actually sends
        fields = ['id','volume', 'price', 'compare_at_price', 'stock']
        list_serializer_class = DashboardVariantListSerializer

    def validate(self, attrs):
        product_id = self.context.get('product_id')
        volume = attrs.get('volume')
        
        if product_id and volume:
            if models.ProductVariant.objects.filter(product_id=product_id, volume=volume).exists():
                raise serializers.ValidationError({"volume": _("A variant with this volume already exists for this product.")})
                
        return attrs

    def create(self, validated_data):
        # We need to manually get the product from the context or the save() call
        # because it's not in the request data
        product_id = self.context['product_id']
        return models.ProductVariant.objects.create(product_id=product_id, **validated_data)




# 3. Create Product Serializer
class DashboardProductCreateSerializer(serializers.ModelSerializer):
    # We include variants here so we can create them in one go if we want
    variants = DashboardVariantCreateSerializer(many=True, required=False)
    
    # Override fields that modeltranslation makes blank=True but should be required
    name_en = serializers.CharField(required=True, allow_blank=False)
    description_en = serializers.CharField(required=True, allow_blank=False)

    # Accept categories by their string names (array)
    categories = serializers.SlugRelatedField(
        slug_field='name',
        queryset=models.Category.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = models.Product
        fields = ['id', 'name_en', 'name_ar', 'categories', 'description_en', 'description_ar', 'fragrance_family_en', 'fragrance_family_ar', 'concentration_en', 'concentration_ar', 'variants', 'is_bestseller']

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        categories_data = validated_data.pop('categories', [])
        
        # Auto-fill Arabic fields with English values if not provided
        for field in ['name', 'description', 'fragrance_family', 'concentration']:
            if not validated_data.get(f'{field}_ar'):
                validated_data[f'{field}_ar'] = validated_data.get(f'{field}_en', '')

        # 1. Create the Product
        product = models.Product.objects.create(**validated_data)
        
        # 2. Assign Categories (M2M)
        if categories_data:
            product.categories.set(categories_data)
        
        # 3. Create the Variants (if any were sent)
        for variant_data in variants_data:
            models.ProductVariant.objects.create(product=product, **variant_data)
            
        return product

class DashboardProductUpdateSerializer(serializers.ModelSerializer):
    # Accept categories by their string names (array)
    categories = serializers.SlugRelatedField(
        slug_field='name',
        queryset=models.Category.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = models.Product
        fields = ['name_en', 'name_ar', 'categories', 'description_en', 'description_ar', 'fragrance_family_en', 'fragrance_family_ar', 'concentration_en', 'concentration_ar', 'is_active', 'is_bestseller']

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)
        for field in ['name', 'description', 'fragrance_family', 'concentration']:
            if validated_data.get(f'{field}_en') and not validated_data.get(f'{field}_ar'):
                validated_data[f'{field}_ar'] = validated_data[f'{field}_en']
        instance = super().update(instance, validated_data)
        if categories_data is not None:
            instance.categories.set(categories_data)
        return instance

class DashboardVariantUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductVariant
        fields = ['volume', 'price', 'compare_at_price', 'stock', 'is_active']
        
    def validate(self, attrs):
        volume = attrs.get('volume')
        
        if volume and self.instance:
            if models.ProductVariant.objects.filter(
                product_id=self.instance.product_id, 
                volume=volume
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({"volume": _("A variant with this volume already exists for this product.")})
                
        return attrs

class BannerSerializer(serializers.ModelSerializer):
    desktop_img_url = serializers.SerializerMethodField()
    mobile_img_url = serializers.SerializerMethodField()
    
    def get_desktop_img_url(self, obj):
        if obj.desktop_image:
            return getattr(obj.desktop_image, 'url', None)
        return None
        
    def get_mobile_img_url(self, obj):
        if obj.mobile_image:
            return getattr(obj.mobile_image, 'url', None)
        return None
        
    class Meta:
        model = models.Banner
        fields = ['id', 'title', 'desktop_image', 'mobile_image', 'desktop_img_url', 'mobile_img_url', 'link', 'is_active', 'order', 'created_at']

class DashboardBannerSerializer(serializers.ModelSerializer):
    desktop_img_url = serializers.SerializerMethodField()
    mobile_img_url = serializers.SerializerMethodField()
    
    def get_desktop_img_url(self, obj):
        if obj.desktop_image:
            return getattr(obj.desktop_image, 'url', None)
        return None
        
    def get_mobile_img_url(self, obj):
        if obj.mobile_image:
            return getattr(obj.mobile_image, 'url', None)
        return None
        
    class Meta:
        model = models.Banner
        fields = ['id', 'title_en', 'title_ar', 'desktop_image', 'mobile_image', 'desktop_img_url', 'mobile_img_url', 'link', 'is_active', 'order', 'created_at']

    def create(self, validated_data):
        if not validated_data.get('title_ar'):
            validated_data['title_ar'] = validated_data.get('title_en', '')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('title_en') and not validated_data.get('title_ar'):
            validated_data['title_ar'] = validated_data['title_en']
        return super().update(instance, validated_data)

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SiteSettings
        fields = ['announcement_text', 'announcement_link', 'is_announcement_active']

class DashboardSiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SiteSettings
        fields = ['announcement_text_en', 'announcement_text_ar', 'announcement_link', 'is_announcement_active']

    def update(self, instance, validated_data):
        if validated_data.get('announcement_text_en') and not validated_data.get('announcement_text_ar'):
            validated_data['announcement_text_ar'] = validated_data['announcement_text_en']
        return super().update(instance, validated_data)

from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except User.DoesNotExist:
            raise InvalidToken(_("User matching this token does not exist."))
