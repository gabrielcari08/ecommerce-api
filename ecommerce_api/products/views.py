from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, permissions as permission
from .serializers import CategoryListSerializer, ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer
from .models import Category, Product

# Create your views here.

#Custom permission to only admins
class IsAdminUser(permission.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'admin'

@api_view(['GET'])
@permission_classes([AllowAny])  #No authentication required
def list_categories(request):
    #Get all categories from the database
    categories = Category.objects.all()

    serializer = CategoryListSerializer(categories, many=True)
    
    return Response({'categories': serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny]) #No authentication required
def list_products(request):

    #Verify that user is authenticated and admin.
    if request.user.is_authenticated and hasattr(request.user, 'user_type') and request.user.user_type == 'admin':
        #The admin can see all te products
        products = Product.objects.all()
    else:
        #The customer users can see only the active products
        products = Product.objects.filter(is_active=True) 
        
            
    #Filter by category if "category_id" is provided in query parameters
    category_id = request.GET.get('category_id')
    if category_id:
        products = products.filter(category__id=category_id)
    
    #Filter by price range if "min_price" and/or "max_price" are provided in query parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
        
    serializer = ProductListSerializer(products, many=True)
    
    return Response({'products': serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail(request, product_id):
  
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    serializer = ProductDetailSerializer(product)
    
    return Response({'product': serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAdminUser]) #Only admins
def create_product(request):
    #Take the JSON data sent in the request
    serializer = ProductCreateUpdateSerializer(data=request.data)
    
    #Verify that serializer is valid
    if serializer.is_valid():
        #The serializer is saves and creates a new product object
        serializer.save()
        
        return Response({"product": serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST )


@api_view(['PUT'])
@permission_classes([IsAdminUser]) #Only admins 
def update_product(request, product_id):
    #Search the product in the database by "product_id"
    product = get_object_or_404(Product, id=product_id)
    
    #with "partial=True" we can send only the fields that we want to change
    serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True)
    
    if serializer.is_valid():
        product = serializer.save()
        
        return Response({"product": serializer.data}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser]) #Only admins         
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    product.delete()
    
    return Response(status=status.HTTP_204_NO_CONTENT)