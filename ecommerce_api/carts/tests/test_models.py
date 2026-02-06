#test of cart models

import pytest
from django.db import IntegrityError
from carts.models import Cart, CartItem
from products.models import Product, Category
from users.models import User

@pytest.mark.django_db
class TestCartModels:
    
    @pytest.fixture
    def sample_user(self):
        """
        User for testing.
        """
        return User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        
    @pytest.fixture
    def sample_category(self):
        """
        Category for testing.
        """
        return Category.objects.create(name='Electronics')
    
    @pytest.fixture
    def sample_product(self, sample_category):
        """
        Product for testing.
        """
        return Product.objects.create(
            name='Smartphone',
            description='A cool smartphone',
            price=699.99,
            category=sample_category
        )
        
    #Test 1: Creating a Cart
    def test_create_cart(self, sample_user):
        """
        Test creating a cart for a user.
        """
        cart = Cart.objects.create(user=sample_user)
        assert cart.user == sample_user
        assert cart.user.username == 'testuser'
        assert cart.user.is_active is True
        
        assert cart.status == 'active'
        
        assert cart.created_at is not None
        assert cart.updated_at is not None
        
        #Verify that cart exists in the database
        assert Cart.objects.filter(user=sample_user).exists()
        
        print("Cart created successfully for user")
        
    #Test 2: A user can have only one cart
    def test_user_single_cart_constraint(self, sample_user):
        """
        Test that a user can only have one cart.
        """
        cart1 = Cart.objects.create(user=sample_user)
        assert cart1.user == sample_user
        
        #Try to create a second cart for the same user
        with pytest.raises(IntegrityError):
            Cart.objects.create(user=sample_user)
            
        print("Test 2 passed: User cannot have multiple carts")