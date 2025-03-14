from django.shortcuts import render, redirect, get_object_or_404
from .models import Pitch, Family, Ostrich, Batch, Egg, FoodPurchase, FoodInventory, Chick, CostCategory, Cost
from .forms import EggForm , FoodPurchaseForm, ChickFromEggForm, ChickFromOutsideForm, CostForm
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum, F

def home(request):
    return render(request, 'home.html')

def farm_settings(request):
    return render(request, 'farm_settings/farm_setting.html')

def eggs(request):
    return render(request, 'eggs/eggs.html')

def chicks(request):
    return render(request, 'chicks.html')

def food(request):
    return render(request, 'food.html')

def extract_report(request):
    return render(request, 'extract_report.html')

def add_pitch(request):
    if request.method == 'POST':
        pitch_number = request.POST.get('pitch_number')
        Pitch.objects.create(pitch_number=pitch_number)
        return redirect('farm_settings')
    return render(request, 'farm_settings/add_pitch.html')

def add_family(request):
    pitches = Pitch.objects.all()
    if request.method == 'POST':
        family_name = request.POST.get('family_name')
        pitch_id = request.POST.get('pitch')
        pitch = Pitch.objects.get(id=pitch_id)
        Family.objects.create(Family_name=family_name, pitch=pitch)
        return redirect('farm_settings')
    return render(request, 'farm_settings/add_family.html', {'pitches': pitches})

def add_ostrich(request):
    families = Family.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        family_id = request.POST.get('family')
        family = Family.objects.get(id=family_id)
        Ostrich.objects.create(name=name, age=age, gender=gender, family=family)
        return redirect('farm_settings')
    return render(request, 'farm_settings/add_ostrich.html', {'families': families})

def add_egg(request):
    if request.method == 'POST':
        form = EggForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('egg_list')
    else:
        form = EggForm()
    return render(request, 'eggs/add_egg.html', {'form': form})

def search_egg(request):
    if request.method == 'POST':
        egg_code = request.POST.get('egg_code')
        try:
            egg = Egg.objects.get(egg_code=egg_code)
            return render(request, 'eggs/egg_detail.html', {'egg': egg})
        except Egg.DoesNotExist:
            error_message = "Egg with this code does not exist."
            return render(request, 'eggs/search_egg.html', {'error_message': error_message})
    return render(request, 'eggs/search_egg.html')

def create_batch(request):
    if request.method == 'POST':
        creation_date_str = request.POST.get('creation_date')  # Get date from form
        egg_codes = request.POST.getlist('egg_codes')  # Get selected egg codes

        # Parse creation_date from string to datetime
        from datetime import datetime
        creation_date = datetime.strptime(creation_date_str, '%Y-%m-%dT%H:%M')

        # Find eggs by codes
        eggs = Egg.objects.filter(egg_code__in=egg_codes)

        # Create batch
        batch = Batch.objects.create(creation_date=creation_date)
        batch.eggs.set(eggs)  # Add eggs to the batch

        return redirect('batch_list')

    eggs = Egg.objects.filter(batch=None)  # Only show eggs not in any batch
    return render(request, 'eggs/create_batch.html', {'eggs': eggs})

def first_check(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    eggs_in_batch = batch.eggs.filter(fertile='Waiting First Check')

    if request.method == 'POST':
        for egg in eggs_in_batch:
            fertile_status = request.POST.get(f'fertile_{egg.id}')
            if fertile_status in ['Fertile', 'Not Fertile']:
                egg.fertile = fertile_status
                egg.save()
        return redirect('batch_list')

    return render(request, 'eggs/first_check.html', {'batch': batch, 'eggs_in_batch': eggs_in_batch})

def egg_list(request):
    # Retrieve all eggs from the database
    eggs = Egg.objects.all().order_by('-lay_date_time')  # Order by lay_date_time in descending order

    # Set up pagination (50 eggs per page)
    paginator = Paginator(eggs, 50)  # Show 50 eggs per page
    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_eggs = paginator.get_page(page_number)  # Get the eggs for the requested page

    return render(request, 'eggs/egg_list.html', {'page_eggs': page_eggs})

def egg_detail(request, egg_code):
    # Retrieve the egg by its unique code
    egg = get_object_or_404(Egg, egg_code=egg_code)

    return render(request, 'eggs/egg_detail.html', {'egg': egg})

def batch_list(request):

    # Retrieve all batches from the database
    batches = Batch.objects.all().order_by('-creation_date')  # Order by creation_date in descending order

    # Set up pagination (20 batches per page)
    paginator = Paginator(batches, 20)  # Show 20 batches per page
    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_batches = paginator.get_page(page_number)  # Get the batches for the requested page

    return render(request, 'eggs/batch_list.html', {'page_batches': page_batches})

def batch_detail(request, batch_id):
    # Retrieve the batch by its ID
    batch = get_object_or_404(Batch, id=batch_id)

    return render(request, 'eggs/batch_detail.html', {'batch': batch})

def add_food_purchase(request):
    if request.method == 'POST':
        form = FoodPurchaseForm(request.POST)
        if form.is_valid():
            form.save()
            # Update the food inventory after adding a purchase
            try:
                FoodInventory.update_inventory()
            except Exception as e:
                print(f"Error updating inventory: {e}")
            return redirect('food_inventory')
    else:
        form = FoodPurchaseForm()

    return render(request, 'food/add_food_purchase.html', {'form': form})

def food_inventory(request):

    # Ensure the FoodInventory object exists
    FoodInventory.objects.get_or_create(id=1, defaults={'current_inventory': 0})

    # Update the food inventory
    try:
        FoodInventory.update_inventory()
    except Exception as e:
        print(f"Error updating inventory: {e}")

    # Get the current inventory and estimated finish date
    try:
        current_inventory = FoodInventory.objects.get(id=1).current_inventory
        finish_date = FoodInventory.estimated_finish_date()
    except FoodInventory.DoesNotExist:
        current_inventory = 0
        finish_date = "No inventory data available."

    context = {
        'current_inventory': current_inventory,
        'finish_date': finish_date,
    }
    return render(request, 'food/food_inventory.html', context)

def add_chick_from_egg(request, egg_id):
    egg = get_object_or_404(Egg, id=egg_id, fertile='Fertile')

    if request.method == 'POST':
        form = ChickFromEggForm(request.POST)
        if form.is_valid():
            chick = form.save(commit=False)
            # chick.pitch = egg.family.pitch  # Assign the same pitch as the egg's family
            chick.save()

            # Mark the egg as used
            egg.fertile = 'Hatched'
            egg.save()

            return redirect('chick_list')
    else:
        form = ChickFromEggForm(initial={'name': f"{egg.egg_code} Chick"})  # Pre-fill the name

    return render(request, 'chicks/add_chick_from_egg.html', {'form': form, 'egg': egg})

def add_chick_outside(request):
    if request.method == 'POST':
        form = ChickFromOutsideForm(request.POST)
        if form.is_valid():
            chick = form.save(commit=False)
            chick.creation_date = timezone.now().date()  # Set creation date to today
            chick.save()
            return redirect('chick_list')
    else:
        form = ChickFromOutsideForm()

    return render(request, 'chicks/add_chick_outside.html', {'form': form})

def chick_list(request):

    chicks = Chick.objects.all().order_by('-creation_date')

    paginator = Paginator(chicks, 20)  # Show 20 chicks per page
    page_number = request.GET.get('page')
    page_chicks = paginator.get_page(page_number)

    return render(request, 'chicks/chick_list.html', {'page_chicks': page_chicks})

def select_egg_for_chick(request):

    fertile_eggs = Egg.objects.filter(fertile='Fertile')
    return render(request, 'chicks/select_egg_for_chick.html', {'fertile_eggs': fertile_eggs})

def add_farm_setting_cost(request):
    # Ensure "Farm Setting Costs" category exists
    farm_setting_category, _ = CostCategory.objects.get_or_create(name="Farm Setting Costs")

    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():  # Check if the form is valid
            cost = form.save(commit=False)
            cost.category = farm_setting_category  # Assign the correct category
            cost.save()  # Save the cost to the database
            return redirect('cost_list')  # Redirect to the cost list page
        else:
            print(form.errors)  # Print form errors for debugging
    else:
        form = CostForm(initial={'category': farm_setting_category})

    return render(request, 'costs/add_farm_setting_cost.html', {'form': form})

def food_costs(request):
    # Calculate the total food cost
    total_food_cost = FoodPurchase.objects.aggregate(total=Sum(F('quantity_kg') * F('price_per_kg')))['total'] or 0

    context = {
        'total_food_cost': total_food_cost,
    }
    return render(request, 'costs/food_costs.html', context)

def add_medical_cost(request):
    # Ensure "Medical Costs" category exists
    medical_category, _ = CostCategory.objects.get_or_create(name="Medical Costs")

    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.category = medical_category  # Assign the correct category
            cost.save()
            return redirect('cost_list')
        else:
            print(form.errors)  # Debug: Print form errors
    else:
        form = CostForm(initial={'category': medical_category})

    return render(request, 'costs/add_medical_cost.html', {'form': form})

def add_rent_tax_cost(request):
    # Ensure "Rent, Taxes" category exists
    rent_tax_category, _ = CostCategory.objects.get_or_create(name="Rent, Taxes")
    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.category = rent_tax_category  # Assign the correct category
            cost.save()
            return redirect('cost_list')
        else:
            print(form.errors)  # Debug: Print form errors
    else:
        form = CostForm(initial={'category': rent_tax_category})
    return render(request, 'costs/add_rent_tax_cost.html', {'form': form})

def add_electricity_water_cost(request):
    # Ensure "Electricity and Water" category exists
    ew_category, _ = CostCategory.objects.get_or_create(name="Electricity and Water")
    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.category = ew_category  # Assign the correct category
            cost.save()
            return redirect('cost_list')
        else:
            print(form.errors)  # Debug: Print form errors
    else:
        form = CostForm(initial={'category': ew_category})
    return render(request, 'costs/add_electricity_water_cost.html', {'form': form})

def add_salary_cost(request):
    # Ensure "Salaries" category exists
    salary_category, _ = CostCategory.objects.get_or_create(name="Salaries")
    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.category = salary_category  # Assign the correct category
            cost.save()
            return redirect('cost_list')
        else:
            print(form.errors)  # Debug: Print form errors
    else:
        form = CostForm(initial={'category': salary_category})
    return render(request, 'costs/add_salary_cost.html', {'form': form})

def add_other_cost(request):
    # Ensure "Other Costs" category exists
    other_category, _ = CostCategory.objects.get_or_create(name="Other Costs")
    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.category = other_category  # Assign the correct category
            cost.save()
            return redirect('cost_list')
        else:
            print(form.errors)  # Debug: Print form errors
    else:
        form = CostForm(initial={'category': other_category})
    return render(request, 'costs/add_other_cost.html', {'form': form})

def cost_list(request):
    # Get all costs
    costs = Cost.objects.all().order_by('-date_paid')

    # Filter by categories if selected
    selected_categories = request.GET.getlist('categories')
    if selected_categories:
        costs = costs.filter(category__id__in=selected_categories)

    # Calculate the total cost for the filtered results
    total_cost = costs.aggregate(total=Sum('price'))['total'] or 0

    # Calculate total costs for all categories
    category_totals = []
    for category in CostCategory.objects.all():
        total = category.costs.aggregate(total=Sum('price'))['total'] or 0
        category_totals.append({
            'category_name': category.name,
            'total': total,
        })

    # Paginate the results
    paginator = Paginator(costs, 20)  # Show 20 costs per page
    page_number = request.GET.get('page')
    page_costs = paginator.get_page(page_number)

    # Get all cost categories for filtering
    categories = CostCategory.objects.all()

    context = {
        'page_costs': page_costs,
        'categories': categories,
        'selected_categories': selected_categories,
        'total_cost': total_cost,
        'category_totals': category_totals,  # Pass the category totals to the template
    }
    return render(request, 'costs/cost_list.html', context)