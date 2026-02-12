from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from carts.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer, CancelOrderSerializer, ReturnOrderSerializer
from products.views import IsAdminUser

# Create your views here.

#This function validates if the status transition is valid
def validate_status_transition(current_status, new_status):
    
        #Valid transitions dictionary
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['return_requested'],
            'cancelled': [],
            'refunded': [],
            'return_requested': ['returned', 'refunded'],
            'returned': []
        }
        
        #Return true if the new status is in the valid transitions for the current status,
        # otherwise return false
        return new_status in valid_transitions.get(current_status, [])

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

@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_order_status(request, order_id):
        
    #Get the order by "order_id"
    #If not found, return 404 error
    order = get_object_or_404(Order, id=order_id)
    
    #Get the new status from the request data
    new_status = request.data.get('status')
    
    #Validate that the new status is provided in the request data
    if not new_status:
        return Response(
            {"message": "El nuevo estado es requerido."},
             status=status.HTTP_400_BAD_REQUEST
            )
    
    #Validate that the new status is valid
    if new_status not in dict(Order.STATUS_CHOICES):
        return Response(
            {"message": "Estado de orden inválido."},
             status=status.HTTP_400_BAD_REQUEST
            )
    
    #Validate that the status transition is valid
    if not validate_status_transition(order.status, new_status):
        #If the function returns False, the transition is not valid
        return Response(
            {"message": f"Transición de estado no válida."},
             status=status.HTTP_400_BAD_REQUEST
            )
    
    #But, the function returns True continue with the code.

    try:
        #Update the order status
        order.status = new_status
        #Save the order
        order.save()
        
        return Response(
            {"message": "Estado de orden actualizado exitosamente."},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                "message": "Error al actualizar el estado de la orden", 
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def request_return(request, order_id):
    
    #Get the order by "order_id" and verify that the order belongs to the user
    #If not found, return 404 error
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    #Verify that the order is delivered
    if order.status != 'delivered':
        return Response(
            {"message": "Solo se pueden solicitar devoluciones para órdenes entregadas."},
             status=status.HTTP_400_BAD_REQUEST
            )
        
    #Verify that the order is in 30 days since the delivery date
    if order.delivered_at < timezone.now() - timezone.timedelta(days=30):
        return Response(
            {"message": "El período para solicitar una devolución ha expirado."},
             status=status.HTTP_400_BAD_REQUEST
            )
    
    #Verify that the order is not already in return requested status
    if order.status == "return_requested":
        return Response(
            {"message": "Ya se ha solicitado una devolución para esta orden."},
             status=status.HTTP_400_BAD_REQUEST
            )
    
    #Verify that the order is not already returned or refunded
    if order.status == "returned" or order.status == "refunded":
        return Response(
            {"message": "Esta orden ya ha sido devuelta o reembolsada."},
             status=status.HTTP_400_BAD_REQUEST
            )
    
    #Validate the serializer data
    serializer = ReturnOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"message": "Datos de devolución inválidos", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        #Set the return reason
        order.return_reason = request.data.get('return_reason')
        #Set the return requested date
        order.return_requested_at = timezone.now()
        #Update the order status to "return_requested"
        order.status = 'return_requested'
        #Save the order
        order.save()
        
        return Response(
            {"message": "Solicitud de devolución enviada exitosamente."},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                "message": "Error al solicitar la devolución",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(['POST'])
@permission_classes([IsAdminUser])
def mark_order_as_delivered(request, order_id):
    #Get the order by "order_id"
    #If not found, return 404 error
    order = get_object_or_404(Order, id=order_id)
    
    #Verify that the order is shipped
    if order.status != 'shipped':
        return Response(
            {"message": "Solo se pueden marcar como entregadas las órdenes que han sido enviadas."},
             status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        #Update the order status to "delivered"
        order.status = 'delivered'
        #Set the delivered date
        order.delivered_at = timezone.now()
        #Save the order
        order.save()
        
        return Response(
            {"message": "Orden marcada como entregada exitosamente."},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                "message": "Error al marcar la orden como entregada", 
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )