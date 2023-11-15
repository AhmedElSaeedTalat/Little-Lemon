from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User, Group

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id' ,'title', 'price', 'featured', 'category', 'category_id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CartSerializer(serializers.ModelSerializer):
    """ 
    serializer to post and display data , when posting only quantity and and menuitem_id is used
    that is while the user is authenticated
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.SerializerMethodField(method_name='get_id')
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    unit_price = serializers.SerializerMethodField(method_name='get_unit_price')
    price = serializers.SerializerMethodField(method_name='calc_price')
    class Meta:
        model = Cart
        fields = ['user', 'user_id', 'menuitem', 'menuitem_id','quantity', 'unit_price', 'price']

    def get_id(self, obj=None):
        if self._context['request'].method == 'POST':
            request = self.context.get('request')
            user_id = request.user.id
            return user_id
        else:
            return obj.user_id
    
    
    def get_unit_price(self, obj=None):
        if self._context['request'].method == 'POST':
            data = self.context['request'].data 
            id = data.get('menuitem_id')
            item = MenuItem.objects.get(pk=id)
            unit_price = item.price
            return unit_price
        else:
            return obj.unit_price
    
    def calc_price(self, obj=None):
        if self._context['request'].method == 'POST':
            quantity = self.context.get('request').data.get('quantity')
            return quantity * self.get_unit_price()
        else:
            return obj.price

    def create(self, validated_data):
        validated_data['user_id'] = self.get_id(None)
        validated_data['unit_price'] = self.get_unit_price(None)
        validated_data['price'] = self.calc_price(None)
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_id', 'delivery_crew', 'status', 'total', 'date']


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = OrderItem
        fields = ['order', 'order_id','menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']