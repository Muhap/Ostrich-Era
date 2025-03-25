
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # General Pages
    path('', views.home, name='home'),
    path('farm-settings/', views.farm_settings, name='farm_settings'),
    path('add-pitch/', views.add_pitch, name='add_pitch'),
    path('add-family/', views.add_family, name='add_family'),
    path('add-ostrich/', views.add_ostrich, name='add_ostrich'),
    path('farm_settings/families/', views.family_list, name='family_list'),
    path('farm_settings/ostriches/', views.ostrich_list, name='ostrich_list'),

    path('eggs/', views.eggs, name='eggs'),
    path('add-egg/', views.add_egg, name='add_egg'),
    path('search-egg/', views.search_egg, name='search_egg'),
    path('create-batch/', views.create_batch, name='create_batch'),
    path('first-check/<int:batch_id>/', views.first_check, name='first_check'),
    path('egg-list/', views.egg_list, name='egg_list'),
    path('egg-detail/<str:egg_code>/', views.egg_detail, name='egg_detail'),
    
    path('batch-list/', views.batch_list, name='batch_list'),
    path('batch-detail/<int:batch_id>/', views.batch_detail, name='batch_detail'),
    path('chicks/', views.chicks, name='chicks'),
    path('add-chick-from-egg/<int:egg_id>/', views.add_chick_from_egg, name='add_chick_from_egg'),
    path('add-chick-outside/', views.add_chick_outside, name='add_chick_outside'),
    path('chick-list/', views.chick_list, name='chick_list'),
    path('select-egg-for-chick/', views.select_egg_for_chick, name='select_egg_for_chick'),

    path('food/', views.food, name='food'),
    path('add-food-purchase/', views.add_food_purchase, name='add_food_purchase'),
    path('food-inventory/', views.food_inventory, name='food_inventory'),

    path('add-farm-setting-cost/', views.add_farm_setting_cost, name='add_farm_setting_cost'),
    path('food-costs/', views.food_costs, name='food_costs'),  
    path('add-medical-cost/', views.add_medical_cost, name='add_medical_cost'),
    path('add-rent-tax-cost/', views.add_rent_tax_cost, name='add_rent_tax_cost'),
    path('add-electricity-water-cost/', views.add_electricity_water_cost, name='add_electricity_water_cost'),
    path('add-salary-cost/', views.add_salary_cost, name='add_salary_cost'),
    path('add-other-cost/', views.add_other_cost, name='add_other_cost'),
    path('cost-list/', views.cost_list, name='cost_list'),
    
    path('sales/add/', views.add_sale, name='add_sale'),
    path('sales/list/', views.sales_list, name='sales_list'),

    path('sales/ostrich/select/', views.select_ostriches, name='select_ostriches'),
    path('sales/ostrich/details/', views.ostrich_sale_details, name='ostrich_sale_details'),
    path('sales/ostrich/review/', views.ostrich_sale_review, name='ostrich_sale_review'),

    path('sales/chick/select/', views.select_chicks, name='select_chicks'),
    path('sales/chick/details/', views.chick_sale_details, name='chick_sale_details'),
    path('sales/chick/review/', views.chick_sale_review, name='chick_sale_review'),


    path('sales/egg/select/', views.select_eggs, name='select_eggs'),
    path('sales/egg/details/', views.egg_sale_details, name='egg_sale_details'),
    path('sales/egg/review/', views.egg_sale_review, name='egg_sale_review'),
    
    path('sales/egg/invoice/<int:sale_id>/', views.generate_egg_invoice, name='generate_egg_invoice'),
    path('sales/chick/invoice/<int:sale_id>/', views.generate_chick_invoice, name='generate_chick_invoice'),
    path('sales/invoice/<int:sale_id>/', views.generate_ostrich_invoice, name='generate_ostrich_invoice'),


    path('extract-report/', views.extract_report, name='extract_report'),

]