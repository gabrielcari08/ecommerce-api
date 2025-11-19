from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemSerializer, CartItemCreateSerializer

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated]) #Only authenticated users can access this view
def get_cart(request):
    #"cart": Cart object
    #"created": Boolean(True: if exists; False: if not)
    #"get_or_create": try to find an existing cart, if not exists, create a new cart automatically
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    #"cart": Cart object
    #"created": Boolean(True: if exists; False: if not)
    #"get_or_create": try to find an existing cart, if not exists, create a new cart automatically
    cart, created = Cart.objects.get_or_create(user=request.user)
    #Data validate
    serializer = CartItemCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Extract validated data
    product_id = serializer.validated_data['product_id'] #For example, product_id = 5
    quantity = serializer.validated_data['quantity'] #For example, quantity = 2

    #Vefify product
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    #Create or update CartItem
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity, 'price': product.price}
    )
    
    #If created = False:
    if not created:
        cart_item.quantity += quantity 
        cart_item.save()
    
    #Serialize updated cart
    cart_serializer = CartSerializer(cart)
    #Return response
    return Response({
        "message": "Producto agregado al carrito",
        "cart": cart_serializer.data
    })