from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'order_number', 'status', 'total_amount',
            'subtotal', 'tax', 'shipping', 'discount', 'shipping_address',
            'shipping_method', 'tracking_number',
            'created_at', 'updated_at', 'items']

        read_only_fields = ['order_number', 'created_at', 'updated_at']
        
class CancelOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['cancellation_reason']
        
class ReturnOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['return_reason']
        
class ProcessReturnSerializer(serializers.Serializer):
    
    ACTION_CHOICES = (
        ('approve', 'Approve Return'),
        ('reject', 'Reject Return'),
    )
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    
    #Validate that if action is 'reject', then rejection_reason must be provided
    def validate(self, data):
        action = data.get('action')
        rejection_reason = data.get('rejection_reason')
        
        if action == 'reject' and not rejection_reason:
            raise serializers.ValidationError(
                "El motivo de rechazo es obligatorio cuando se rechaza una devolución."
                )
        
        return data