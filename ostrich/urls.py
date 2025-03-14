
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
    path('add-farm-setting-cost/', views.add_farm_setting_cost, name='add_farm_setting_cost'),
    path('food-costs/', views.food_costs, name='food_costs'),
    path('add-medical-cost/', views.add_medical_cost, name='add_medical_cost'),
    path('add-rent-tax-cost/', views.add_rent_tax_cost, name='add_rent_tax_cost'),
    path('add-electricity-water-cost/', views.add_electricity_water_cost, name='add_electricity_water_cost'),
    path('add-salary-cost/', views.add_salary_cost, name='add_salary_cost'),
    path('add-other-cost/', views.add_other_cost, name='add_other_cost'),
    path('cost-list/', views.cost_list, name='cost_list'),
]