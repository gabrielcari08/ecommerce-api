from django.shortcuts import render, get_object_or_404
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from carts.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer


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

