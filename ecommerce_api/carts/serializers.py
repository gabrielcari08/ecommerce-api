from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductListSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'price']
        read_only_fields = ['id', 'price']  #Protect the auto-generated fields and price
        
class CartItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']
    
    #Validate that quantity is positive
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser al menos 1.")
        return value
    
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True, source='cartitem_set')
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'status', 'created_at', 'updated_at', 
                 'items', 'total_items', 'total_price']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 
                          'total_items', 'total_price']

class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser al menos 1.")
        return value