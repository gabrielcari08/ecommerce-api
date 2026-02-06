#test of products models

import pytest
from django.core.exceptions import ValidationError
from products.models import Product, Category

@pytest.mark.django_db #Thos decorator is necessary to access the database in tests
class TestCategoryModel:
    
    """
    This class groups all the tests related to the Category model.
    """
    
    #Test 1: Test category creation
    def test_create_category(self):
        
        """
        Objective: Verify that a Category instance can be created successfully.
        
        Input: Name "Electronics"
        Process: Category.objects.create(name="Electronics")
        Outuput:
        - category.name == "Electronics"
        - The category exists in the database
        """
        
        #ACT: Create the category
        category = Category.objects.create(name="Electronics")
        
        #ASSERT: Verify the category was created correctly
        assert category.name == "Electronics"
        #Also, verify it exists in the database
        assert Category.objects.filter(name="Electronics").exists()
        
    #Test 2:
    
    def test_category_str_method(self):
        
        """
        Objective: Verify that the __str__ method of the Category model returns the correct string representation.
        
        Input: Name "Books"
        Process: str(category)
        Output: "Books"
        """
        
        #ARRANGE: Create a category instance
        category = Category(name="Books")
        
        assert str(category) == "Books"
        
    #Test 3:
    
    def test_category_table_name(self):
        
        """
        Objective: Verify that the Category model has the correct database table name.
        
        """
        
        #Verify the table name
        assert Category._meta.db_table == "categories"
        
        
@pytest.mark.django_db
class TestProductModel:
    """
    Tests to product model
    """
    
    @pytest.fixture
    def sample_category(self):
        return Category.objects.create(name="Test Category")
    
    #Test 1: Test product creation
    def test_create_product_with_category(self, sample_category):
        
        """
        Objective: Verify that a Product instance can be created successfully.
        
        Input:
        - name: "Laptop"
        - description: "A high-performance laptop"
        - price: 999.99
        - stock: 10
        - category: sample_category
        
        Process: Product.objects.create(...)
        
        Output:
        - product attributes match input values
        - The product exists in the database
        """
        
        #ACT: Create the product
        product = Product.objects.create(
            name="Laptop",
            description="A high-performance laptop",
            price=999.99,
            category=sample_category
        )
        
        #ASSERT: Verify the product was created correctly
        assert product.name == "Laptop"
        assert product.description == "A high-performance laptop"
        assert product.price == 999.99
        assert product.category == sample_category
        
        #Also, verify it exists in the database
        assert Product.objects.filter(name="Laptop").exists()
      
        
    #Test 2: Product without category.
    def test_product_without_category(self):
        
        """
        Objective: Verify the creation of Product without a category.
        """
        
        #Dont use fixture here
        product = Product.objects.create(
            name="Smartphone",
            description="A latest model smartphone",
            price=699.99
        )
        
        assert product.category is None
        assert product.name == "Smartphone"
        
    #Test 3: Price can be null
    def test_product_price_can_be_null(self, sample_category):
        
        """
        Objective: Verify that a Product can be created with a null price.
        """
        
        product = Product.objects.create(
            name="Headphones",
            description="Noise-cancelling headphones",
            price=None,
            category=sample_category
        )
        
        assert product.price is None
        assert product.name == "Headphones"
        
    #Test 4: Value "is_active" default true
    def test_product_is_active_default_true(self, sample_category):
        
        """
        Objective: Verify that the is_active field defaults to True.
        """
        
        product = Product.objects.create(
            name="Tablet",
            description="A lightweight tablet",
            price=299.99,
            category=sample_category
        )
        
        assert product.is_active is True
    