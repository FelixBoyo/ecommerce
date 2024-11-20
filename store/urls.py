from django.urls import path

from . import views
from django.contrib.auth import views as auth_view

from .views import signup

urlpatterns = [
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('signup/',views.signup, name="signup"),
    path('login/', auth_view.LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('logout/', auth_view.LogoutView.as_view(), name='logout'),
    ]