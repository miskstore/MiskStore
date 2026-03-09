from rest_framework import serializers
from base import models

class GetAllProductListSerializer(serializers.ModelSerializer):
    # We will calculate these in the View using SQL annotations for speed
    lowest_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = [
            'id', 
            'name', 
            'category_name', 
            'lowest_price', # e.g., "From $10.00"
            'average_rating', 
            'review_count',
            'thumbnail', 
            'created_at',
            'is_active'
        ]

    def get_thumbnail(self, obj):
        # Efficiently grab the first image from the pre-fetched variants
        # logic: Get first variant -> Get first image of that variant
        first_variant = next(iter(obj.variants.all()), None)
        if first_variant:
            first_image = next(iter(first_variant.images.all()), None)
            if first_image and first_image.img:
                return first_image.img.url 
        return None # Return placeholder URL if needed


class VariantSerializer(serializers.ModelSerializer):
    # Flatten the image URL list for the frontend
    images = serializers.SerializerMethodField()
    product_name = serializers.CharField(source="product.name", read_only=True)
    category_name = serializers.CharField(source='product.category.name',read_only=True)
    class Meta:
        model = models.ProductVariant
        fields = ['id','product_name','category_name', 'volume', 'price', 
                  'compare_at_price', 'stock', 'images', 'is_on_sale','is_active']

    def get_images(self, obj):
        # Returns a list of dictionaries: [{"id": 1, "url": "cloud/img1.jpg"}, ...]
        return [{"id": img.id, "url": img.img.url,"is_thumbnail":img.is_thumbnail} for img in obj.images.all() if img.img]

class ProductDetailSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True, read_only=True)
    
    # THE FIX: ReadOnlyField safely catches the error. 
    # If category is missing, it just returns `null` in the JSON instead of crashing!
    category = serializers.ReadOnlyField(source='category.name')
    
    
    # Aggregate data for the main header
    rating = serializers.FloatField(source='average_rating_value', read_only=True)

    class Meta:
        model = models.Product
        fields = [
            'id', 'name', 'description', 'category', 'fragrance_family', 'concentration', 
            'variants', 'rating', 'created_at'
        ]


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
        fields = ['id', 'name'] 
        # Add 'description' or 'slug' here if your model has them

class OrderItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(source='variant.product.name', read_only=True)
    variant_volume = serializers.CharField(source='variant.volume', read_only=True)
    
    class Meta:
        model = models.OrderItem
        fields = ['variant_name','variant_volume', 'quantity', 'price', 'subtotal','created_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.Order
        fields = ['id', 'status', 'total_price', 'created_at', 'items', 
                  'full_name', 'full_address', 'phone_number', 'country']
        read_only_fields = ['id', 'status', 'total_price', 'created_at', 'items']

class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['full_name', 'full_address', 'phone_number', 'country', 'order_notes']

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
        # Unique check is enforced at DB level, but good to validate here too
        request = self.context.get('request')
        if models.Review.objects.filter(customer=request.user, product=data['product']).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
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
        valid_statuses = ["cancelled", "delivered", "shipped", "paid", "pending"]
        if value not in valid_statuses:
            raise serializers.ValidationError("Invalid status choice.")
        
        # 2. Check logic (e.g., can't manually set to paid)
        if value == 'paid':
             raise serializers.ValidationError("You cannot manually mark an order as Paid. Use the Payment endpoint.")
        
        # 3. Check current status (instance access)
        if self.instance.status == 'paid':
             raise serializers.ValidationError("Cannot change status of a paid order.")
             
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
    
    class Meta:
        model = models.Order
        fields = ['id', 'status', 'total_price', 'created_at', 'items', 
                  'full_name', 'full_address', 'phone_number', 'country']
        read_only_fields = ['id', 'status', 'total_price', 'created_at', 'items']

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
            raise serializers.ValidationError("Duplicate volumes are not allowed in the same request.")
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
                raise serializers.ValidationError({"volume": f"A variant with volume '{volume}' already exists for this product."})
                
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
    
    # Accept the category by its string name instead of ID
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=models.Category.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = models.Product
        fields = ['id', 'name', 'category', 'description', 'fragrance_family', 'concentration', 'variants']

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        
        # 1. Create the Product
        product = models.Product.objects.create(**validated_data)
        
        # 2. Create the Variants (if any were sent)
        for variant_data in variants_data:
            models.ProductVariant.objects.create(product=product, **variant_data)
            
        return product

class DashboardProductUpdateSerializer(serializers.ModelSerializer):
    # 1. We override the default category field
    category = serializers.SlugRelatedField(
        slug_field='name',                       # Look up the category by its 'name'
        queryset=models.Category.objects.all(),  # Search in the Category table
        allow_null=True,                         # Fixes that "NoneType" crash you just had!
        required=False                           # Crucial because PATCH requests might not include the category
    )

    class Meta:
        model = models.Product
        fields = ['name', 'category', 'description', 'fragrance_family', 'concentration', 'is_active']

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
                raise serializers.ValidationError({"volume": f"A variant with volume '{volume}' already exists for this product."})
                
        return attrs

