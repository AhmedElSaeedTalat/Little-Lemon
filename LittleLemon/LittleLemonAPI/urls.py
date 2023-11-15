from django.urls import path, include
from . import views
from . import user_views
from . import orders_views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:menuItem>', views.MenuItemsView.as_view()),
    path('obtainatoken/', obtain_auth_token),
    path('groups/manager/users/', user_views.UsersView.as_view()),
    path('groups/manager/users/<int:userId>', user_views.UsersView.as_view()),
    path('groups/delivery-crew/users', user_views.DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:userId>', user_views.DeliveryCrewView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders/', orders_views.OrderView.as_view()),
    path('orders/<int:orderId>',orders_views.OrderView.as_view())
]