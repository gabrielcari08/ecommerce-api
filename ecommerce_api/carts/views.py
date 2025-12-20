from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemSerializer, CartItemCreateSerializer, CartItemUpdateSerializer

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

    #Verify stock availability
    if quantity > 100: #Assuming each product has a stock of 100 for simplicity
        return Response(
            {"detail": "Cantidad solicitada excede el stock disponible."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
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
   
#Update cart item quantity 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    
    #Verify that the cart item exists and belongs to the user's cart
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response(
            {"detail": "Elemento del carrito no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    #Validate data
    serializer = CartItemUpdateSerializer(cart_item, data=request.data)
    #If data is not valid...
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Excract the quantity
    quantity = serializer.validated_data['quantity']
    
    if quantity > 100: #Assuming each product has a stock of 100 for simplicity
        return Response(
            {"detail": "Cantidad solicitada excede el stock disponible."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    #Update the quantity and save
    cart_item.quantity = quantity
    cart_item.save()
    
    cart_serializer = CartSerializer(cart_item.cart)
    return Response({
        "message": "Elemento del carrito actualizado",
        "cart": cart_serializer.data
    })

#Delete cart item
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    
    #Verify that the cart item exists and belongs to the user's cart
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response(
            {"detail": "Elemento del carrito no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    #If the quantity is greater than 1, decrement it by 1
    if cart_item.quantity > 1:
        #Decrement the quantity by 1
        cart_item.quantity -= 1
        #Save the cart item
        cart_item.save()
        message = "Elemento del carrito actualizado"
    #If the quantity is 1, delete the cart item
    else:
        #Delete the cart item
        cart_item.delete()
        message = "Elemento eliminado del carrito"
    
    #Response with updated cart
    cart_serializer = CartSerializer(cart_item.cart)
    return Response({
        "message": message,
        "cart": cart_serializer.data
    })
    
#Clear the cart
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    
    #Verify that the cart exists
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return Response(
            {"detail": "Carrito no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    #Delete all items in the cart
    cart.cartitem_set.all().delete()
    
    #Response with updated cart
    cart_serializer = CartSerializer(cart)
    return Response({
        "message": "Carrito vaciado",
        "cart": cart_serializer.data
    })
  
#Cart summary view  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_summary(request):
    
    #Get or create the cart for the authenticated user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    return Response({
        "total_items": cart.total_items,
        "total_price": cart.total_price,
        "items_count": cart.cartitem_set.count()
    })