from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from carts.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer, CancelOrderSerializer

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_order_from_cart(request):
    
    try:
    #Get the user cart
        cart = Cart.objects.select_for_update().get(user=request.user, status="active")
    except Cart.DoesNotExist:
        return Response(
            {"message": "No se encontró un carrito activo para el usuario"},
             status=status.HTTP_404_NOT_FOUND
            )         

    #Validate that user cart has items
    if cart.cartitem_set.count() == 0:
        return Response(
            {"message": "El carrito está vacío"},
             status=status.HTTP_400_BAD_REQUEST
            )
        
    #Validate that the shipping address is provided in the request data
    if not request.data.get('shipping_address'):
        return Response(
            {"message": "La dirección de envío es requerida"},
             status=status.HTTP_400_BAD_REQUEST
            )
    
    #Validate that the billing address is provided in the request data
    if not request.data.get('billing_address'):
        return Response(
            {"message": "La dirección de facturación es requerida"},
             status=status.HTTP_400_BAD_REQUEST
            )

    try:
        #Create an order
        order = Order.objects.create(
            user=request.user,
            status="pending",
            subtotal=cart.total_price,
            total_amount=cart.total_price,
            shipping_address=request.data.get('shipping_address', {}),
            billing_address=request.data.get('billing_address', {}),
        )

        #Convert cart items
        order_items = []
        for cart_item in cart.cartitem_set.all():
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                unit_price=cart_item.price,
                total_price=cart_item.quantity * cart_item.price,
            )
            order_items.append(order_item)

        #Delete cart items
        cart.cartitem_set.all().delete()
        #Update cart status
        cart.status = "converted"
        #Save cart
        cart.save()

        serializer = OrderSerializer(order)
        return Response(
            {
                "message": "Orden creada exitosamente",
                "order": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {
                "message": "Error al crear la orden",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_detail(request, order_id):
    #Get the order by "order_id" and verify that the order belongs to the user
    #If not found, return 404 error
    order = get_object_or_404(Order, id=order_id, user=request.user)
    serializer = OrderSerializer(order)
    return Response(serializer.data)    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    #Verify that the order is not already shipped, delivered, cancelled or refunded
    if order.status in ['shipped', 'delivered', 'cancelled', 'refunded']:
        return Response(
            {"message": "No se puede cancelar una orden que ya ha sido enviada, entregada, cancelada o reembolsada."},
             status=status.HTTP_400_BAD_REQUEST
            )
        
    #Validate the serializer data
    serializer = CancelOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"message": "Datos de cancelación inválidos", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        #Set the return reason
        order.return_reason = request.data.get('return_reason')
        #Set the return requested date
        order.return_requested_at = timezone.now()
        #Cancel the order
        order.status = 'cancelled'
        #Save the order
        order.save()
        
        return Response(
            {"message": "Orden cancelada exitosamente."},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            {
                "message": "Error al cancelar la orden",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_summary(request):
    
    #Get de user orders
    orders = Order.objects.filter(user=request.user)
    
    #Response
    return Response({
        "total_orders": orders.count(),
        "orders_by_status": {
            "pending": orders.filter(status='pending').count(),
            "confirmed": orders.filter(status='confirmed').count(),
            "processing": orders.filter(status='processing').count(),
            "shipped": orders.filter(status='shipped').count(),
            "delivered": orders.filter(status='delivered').count(),
            "cancelled": orders.filter(status='cancelled').count(),
            "refunded": orders.filter(status='refunded').count(),
            },
        "total_spent": sum(order.total_amount for order in orders),
        "average_order_value": sum(order.total_amount for order in orders) / orders.count() 
        if orders.count() > 0 else 0,
        "recent_orders": OrderSerializer(orders.order_by('-created_at')[:5], many=True).data
    })