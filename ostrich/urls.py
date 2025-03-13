
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('farm-settings/', views.farm_settings, name='farm_settings'),
    path('eggs/', views.eggs, name='eggs'),
    path('chicks/', views.chicks, name='chicks'),
    path('food/', views.food, name='food'),
    path('extract-report/', views.extract_report, name='extract_report'),
    path('add-pitch/', views.add_pitch, name='add_pitch'),
    path('add-family/', views.add_family, name='add_family'),
    path('add-ostrich/', views.add_ostrich, name='add_ostrich'),
    path('add-egg/', views.add_egg, name='add_egg'),
    path('search-egg/', views.search_egg, name='search_egg'),
    path('create-batch/', views.create_batch, name='create_batch'),
    path('first-check/<int:batch_id>/', views.first_check, name='first_check'),
    path('egg-list/', views.egg_list, name='egg_list'),
    path('egg-detail/<str:egg_code>/', views.egg_detail, name='egg_detail'),
    path('batch-list/', views.batch_list, name='batch_list'),
    path('batch-detail/<int:batch_id>/', views.batch_detail, name='batch_detail'),
    path('add-food-purchase/', views.add_food_purchase, name='add_food_purchase'),
    path('food-inventory/', views.food_inventory, name='food_inventory'),
    path('add-chick-from-egg/<int:egg_id>/', views.add_chick_from_egg, name='add_chick_from_egg'),
    path('add-chick-outside/', views.add_chick_outside, name='add_chick_outside'),
    path('chick-list/', views.chick_list, name='chick_list'),
    path('select-egg-for-chick/', views.select_egg_for_chick, name='select_egg_for_chick'),
]