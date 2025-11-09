from rest_framework import serializers
from .models import Product, Category

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id'] #Protect the auto-generated field
        
class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category_name', 'price', 'created_at']
        read_only_fields = ['id', 'created_at'] #Protect the auto-generated fields
        
class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description', 'price', 'created_at']
        read_only_fields = ['id', 'created_at'] #Protect the auto-generated fields
        
class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name'  #Use the name field to represent the category
    )
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'is_active']
        
    def validate_price(self, value):
        if value < 0:
             raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value
        
    def validate_category(self, value):
        #Verify that category exists by id
        if not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("La categoría no existe")
        return value
