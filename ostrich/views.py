from django.shortcuts import render, redirect, get_object_or_404
from .models import Pitch, Family, Ostrich, Batch, Egg, FoodPurchase, FoodInventory, Chick, CostCategory, Cost,OstrichSale ,EggSale, ChickSale
from .forms import EggForm , FoodPurchaseForm, ChickFromEggForm, ChickFromOutsideForm, CostForm, SaleForm,OstrichSelectionForm,EggSelectionForm,ChickSelectionForm
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum, F
from django.db import IntegrityError

def home(request):
    piches_count = Pitch.objects.all().count()
    ostrich_count = Ostrich.objects.all().filter(status = 'exists').count()
    chick_count = Chick.objects.all().filter(status = 'exists').count()
    Context = {
        'piches_count': piches_count,
        'ostrich_count': ostrich_count,
        'chick_count': chick_count
    }
    return render(request, 'home.html', Context)

def farm_settings(request):
    return render(request, 'farm_settings/farm_setting.html')

def eggs(request):
    return render(request, 'eggs/eggs.html')

def chicks(request):
    return render(request, 'chicks.html')

def extract_report(request):
    return render(request, 'extract_report.html')

def add_pitch(request):
    if request.method == 'POST':
        pitch_number = request.POST.get('pitch_number')

        # Check if pitch number already exists
        if Pitch.objects.filter(pitch_number=pitch_number).exists():
            messages.error(request, f"Pitch number {pitch_number} already exists!")
            return render(request, 'farm_settings/add_pitch.html')

        try:
            Pitch.objects.create(pitch_number=pitch_number)
            messages.success(request, "Pitch added successfully!")
            return redirect('home')
        except IntegrityError:
            messages.error(request, "An error occurred while adding the pitch. Please try again.")

    return render(request, 'farm_settings/add_pitch.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Pitch, Family, Ostrich

def add_family(request):
    pitches = Pitch.objects.all()

    if request.method == 'POST':
        family_name = request.POST.get('family_name')
        pitch_id = request.POST.get('pitch')

        # Ensure pitch exists
        pitch = get_object_or_404(Pitch, id=pitch_id)

        # Check if family name already exists in the selected pitch
        if Family.objects.filter(Family_name=family_name, pitch=pitch).exists():
            messages.error(request, f"Family '{family_name}' already exists in Pitch {pitch.pitch_number}!")
            return render(request, 'farm_settings/add_family.html', {'pitches': pitches})

        # Create family
        Family.objects.create(Family_name=family_name, pitch=pitch)
        messages.success(request, f"Family '{family_name}' added successfully!")
        return redirect('family_list.html')

    return render(request, 'farm_settings/add_family.html', {'pitches': pitches})

def add_ostrich(request):
    families = Family.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        family_id = request.POST.get('family')

        family = get_object_or_404(Family, id=family_id)

        # Create ostrich and save
        Ostrich.objects.create(name=name, age=age, gender=gender, family=family)
        
        messages.success(request, "Ostrich added successfully!")
        return redirect('ostrich_list')  # Ensure 'ostrich_list' is a valid URL name

    return render(request, 'farm_settings/add_ostrich.html', {'families': families})

def family_list(request):
    families = Family.objects.filter(ostriches__status="exists").distinct().order_by('pitch__pitch_number', 'Family_name')
    paginator = Paginator(families, 10)  # Show 10 families per page
    page_number = request.GET.get('page')
    page_families = paginator.get_page(page_number)

    return render(request, 'farm_settings/family_list.html', {'families': page_families})

def ostrich_list(request):
    ostriches = Ostrich.objects.all().filter(status = 'exists').order_by('family__Family_name', 'name')
    
    paginator = Paginator(ostriches, 10)  # Show 10 ostriches per page
    page_number = request.GET.get('page')
    page_ostriches = paginator.get_page(page_number)

    return render(request, 'farm_settings/ostrich_list.html', {'ostriches': page_ostriches})

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

def food(request):
    return render(request, 'food.html')

def food_costs(request):
    # Calculate the total food cost
    total_food_cost = FoodPurchase.objects.aggregate(total=Sum(F('quantity_kg') * F('price_per_kg')))['total'] or 0
    context = {
        'total_food_cost': total_food_cost,
    }
    return render(request, 'costs/food_costs.html', context)

def add_food_purchase(request):
    if request.method == 'POST':
        form = FoodPurchaseForm(request.POST)
        if form.is_valid():
            food_purchase = form.save()  # Save the food purchase

            # Create a corresponding Cost entry
            food_cost_category, _ = CostCategory.objects.get_or_create(name="Food Costs")
            Cost.objects.create(
                name=f"Food Purchase - {food_purchase.purchase_date}",
                price=food_purchase.quantity_kg * food_purchase.price_per_kg,
                category=food_cost_category,
                date_paid=food_purchase.purchase_date,
                notes=f"Food purchase of {food_purchase.quantity_kg} kg at ج.م{food_purchase.price_per_kg}/kg",
            )

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
    FoodInventory.objects.get_or_create(id=1, defaults={'current_inventory': 0})
    try:
        FoodInventory.update_inventory()
    except Exception as e:
        print(f"Error updating inventory: {e}")
    try:
        current_inventory = FoodInventory.objects.get(id=1).current_inventory
        finish_date = FoodInventory.estimated_finish_date()
    except FoodInventory.DoesNotExist:
        current_inventory = 0
        finish_date = "No inventory data available."
    total_adult_ostriches = Ostrich.objects.all().count() + Chick.total_adult_chicks()
    context = {
        'current_inventory': current_inventory,
        'finish_date': finish_date,
        'total_adult_ostriches': total_adult_ostriches
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

    paginator = Paginator(chicks, 10)  # Show 10 chicks per page
    page_number = request.GET.get('page')
    page_chicks = paginator.get_page(page_number)

    return render(request, 'chicks/chick_list.html', {'page_chicks': page_chicks})  # Remove 'chicks'


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
        'category_totals': category_totals,
    }
    return render(request, 'costs/cost_list.html', context)

def add_sale(request):
    form = SaleForm(request.POST or None, request=request)

    if request.method == 'POST' and form.is_valid():
        sale = form.save(commit=False)

        # Ensure correct item is selected based on category
        if sale.category == "egg":
            sale.chick = None
            sale.ostrich = None
        elif sale.category == "chick":
            sale.egg = None
            sale.ostrich = None
        elif sale.category == "ostrich":
            sale.egg = None
            sale.chick = None

        sale.save()
        messages.success(request, "Sale recorded successfully!")
        return redirect('sales_list')

    return render(request, 'sales/add_sale.html', {'form': form})

from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Sum
from .models import OstrichSale, ChickSale, EggSale

def sales_list(request):
    # Combine all sales into a single list
    ostrich_sales = OstrichSale.objects.all().values('id', 'invoice_number', 'ostrich__name', 'weight_kg', 'price', 'sale_date')
    chick_sales = ChickSale.objects.all().values('id', 'invoice_number', 'chick__name', 'price', 'sale_date')
    egg_sales = EggSale.objects.all().values('id', 'invoice_number', 'egg__egg_code', 'price', 'sale_date')

    all_sales = []

    for sale in ostrich_sales:
        all_sales.append({
            'id': sale['id'],
            'invoice_number': sale['invoice_number'],
            'item': sale['ostrich__name'],
            'weight': sale['weight_kg'],
            'price': sale['price'],
            'sale_date': sale['sale_date'],
            'category': 'Ostrich'
        })

    for sale in chick_sales:
        all_sales.append({
            'id': sale['id'],
            'invoice_number': sale['invoice_number'],
            'item': sale['chick__name'],
            'weight': None,  # Chicks do not have weight in sales
            'price': sale['price'],
            'sale_date': sale['sale_date'],
            'category': 'Chick'
        })

    for sale in egg_sales:
        all_sales.append({
            'id': sale['id'],
            'invoice_number': sale['invoice_number'],
            'item': sale['egg__egg_code'],
            'weight': None,  # Eggs do not have weight in sales
            'price': sale['price'],
            'sale_date': sale['sale_date'],
            'category': 'Egg'
        })

    # Filtering by category
    selected_categories = request.GET.getlist('categories')
    if selected_categories:
        all_sales = [sale for sale in all_sales if sale['category'] in selected_categories]

    # Sorting sales by sale_date (newest first)
    all_sales = sorted(all_sales, key=lambda x: x['sale_date'], reverse=True)

    # Pagination
    paginator = Paginator(all_sales, 10)  # 10 sales per page
    page_number = request.GET.get('page')
    page_sales = paginator.get_page(page_number)

    # Calculate total revenue
    total_revenue = sum(sale['price'] for sale in all_sales)

    # Category totals
    category_totals = []
    for category in ['Ostrich', 'Chick', 'Egg']:
        category_total = sum(sale['price'] for sale in all_sales if sale['category'] == category)
        category_totals.append({'category_name': category, 'total': category_total})

    context = {
        'page_sales': page_sales,
        'total_revenue': total_revenue,
        'category_totals': category_totals,
        'selected_categories': selected_categories,
    }

    return render(request, 'sales/sales_list.html', context)


from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
# Step 1: Select Ostriches
def select_ostriches(request):
    if request.method == "POST":
        form = OstrichSelectionForm(request.POST)
        if form.is_valid():
            request.session['selected_ostriches'] = list(form.cleaned_data['ostriches'].values_list('id', flat=True))
            return redirect('ostrich_sale_details')
    else:
        form = OstrichSelectionForm()

    return render(request, 'sales/select_ostriches.html', {'form': form})
# Step 2: Enter Ostrich Sale Details
def ostrich_sale_details(request):
    selected_ostrich_ids = request.session.get('selected_ostriches', [])
    ostriches = Ostrich.objects.filter(id__in=selected_ostrich_ids)

    if request.method == "POST":
        sale_data = []
        for ostrich in ostriches:
            weight = request.POST.get(f'weight_{ostrich.id}')
            price = request.POST.get(f'price_{ostrich.id}')
            if weight and price:
                sale_data.append({
                    'ostrich_id': ostrich.id,
                    'weight_kg': weight,
                    'price': price
                })

        request.session['ostrich_sale_data'] = sale_data
        return redirect('ostrich_sale_review')

    return render(request, 'sales/ostrich_sale_details.html', {'ostriches': ostriches})
# Step 3: Review & Confirm Sale
def ostrich_sale_review(request):
    sale_data = request.session.get('ostrich_sale_data', [])
    ostriches = Ostrich.objects.filter(id__in=[item['ostrich_id'] for item in sale_data])

    # Zip ostrich objects with their sale data before passing to the template
    ostrich_sale_pairs = []
    for ostrich in ostriches:
        for data in sale_data:
            if ostrich.id == data['ostrich_id']:
                ostrich_sale_pairs.append({'ostrich': ostrich, 'weight_kg': data['weight_kg'], 'price': data['price']})

    if request.method == "POST":
        invoice_number = f"INV-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        for item in sale_data:
            ostrich = Ostrich.objects.get(id=item['ostrich_id'])
            OstrichSale.objects.create(
                ostrich=ostrich,
                weight_kg=item['weight_kg'],
                price=item['price'],
                invoice_number=invoice_number
            )
            ostrich.status = "sold"
            ostrich.save()

        messages.success(request, "Sale completed successfully!")
        return redirect('sales_list')

    return render(request, 'sales/ostrich_sale_review.html', {'ostrich_sale_pairs': ostrich_sale_pairs})

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404

def generate_ostrich_invoice(request, sale_id):
    sale = get_object_or_404(OstrichSale, id=sale_id)

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{sale.invoice_number}.pdf"'

    # Create the PDF
    pdf = canvas.Canvas(response, pagesize=A4)
    pdf.setTitle(f"Invoice {sale.invoice_number}")

    # Invoice Title
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(200, 800, f"Invoice - {sale.invoice_number}")

    # Sale Details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 750, f"Sale Date: {sale.sale_date}")
    pdf.drawString(100, 720, f"Ostrich Name: {sale.ostrich.name}")
    pdf.drawString(100, 690, f"Weight: {sale.weight_kg} kg")
    pdf.drawString(100, 660, f"Price: {sale.price} L.E")

    # Footer
    pdf.line(100, 640, 500, 640)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, 620, f"Total: {sale.price} L.E")

    # Finalize PDF
    pdf.showPage()
    pdf.save()

    return response

def select_chicks(request):
    if request.method == "POST":
        form = ChickSelectionForm(request.POST)
        if form.is_valid():
            request.session['selected_chicks'] = list(form.cleaned_data['chicks'].values_list('id', flat=True))
            return redirect('chick_sale_details')
    else:
        form = ChickSelectionForm()

    return render(request, 'sales/select_chicks.html', {'form': form})

def chick_sale_details(request):
    selected_chick_ids = request.session.get('selected_chicks', [])
    chicks = Chick.objects.filter(id__in=selected_chick_ids)

    if request.method == "POST":
        sale_data = []
        for chick in chicks:
            price = request.POST.get(f'price_{chick.id}')
            if price:
                sale_data.append({'chick_id': chick.id, 'price': price})

        request.session['chick_sale_data'] = sale_data
        return redirect('chick_sale_review')

    return render(request, 'sales/chick_sale_details.html', {'chicks': chicks})
def chick_sale_review(request):
    sale_data = request.session.get('chick_sale_data', [])
    chicks = Chick.objects.filter(id__in=[item['chick_id'] for item in sale_data])

    # Prepare data as a list of dictionaries
    chick_sale_pairs = []
    for chick in chicks:
        for item in sale_data:
            if chick.id == item['chick_id']:
                chick_sale_pairs.append({'chick': chick, 'price': item['price']})

    if request.method == "POST":
        invoice_number = f"INV-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        for item in sale_data:
            chick = Chick.objects.get(id=item['chick_id'])
            ChickSale.objects.create(
                chick=chick,
                price=item['price'],
                invoice_number=invoice_number
            )
            chick.status = "sold"
            chick.save()

        messages.success(request, "Chick sale completed successfully!")
        return redirect('sales_list')

    return render(request, 'sales/chick_sale_review.html', {'chick_sale_pairs': chick_sale_pairs})


def select_eggs(request):
    if request.method == "POST":
        form = EggSelectionForm(request.POST)
        if form.is_valid():
            request.session['selected_eggs'] = list(form.cleaned_data['eggs'].values_list('id', flat=True))
            return redirect('egg_sale_details')
    else:
        form = EggSelectionForm()

    return render(request, 'sales/select_eggs.html', {'form': form})

def egg_sale_details(request):
    selected_egg_ids = request.session.get('selected_eggs', [])
    eggs = Egg.objects.filter(id__in=selected_egg_ids)

    if request.method == "POST":
        sale_data = []
        for egg in eggs:
            price = request.POST.get(f'price_{egg.id}')
            if price:
                sale_data.append({'egg_id': egg.id, 'price': price})

        request.session['egg_sale_data'] = sale_data
        return redirect('egg_sale_review')

    return render(request, 'sales/egg_sale_details.html', {'eggs': eggs})

def egg_sale_review(request):
    sale_data = request.session.get('egg_sale_data', [])
    eggs = Egg.objects.filter(id__in=[item['egg_id'] for item in sale_data])

    # Prepare sale data in a structured list
    egg_sale_pairs = []
    for egg in eggs:
        for item in sale_data:
            if egg.id == item['egg_id']:
                egg_sale_pairs.append({'egg': egg, 'price': item['price']})

    if request.method == "POST":
        invoice_number = f"INV-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        for item in sale_data:
            egg = Egg.objects.get(id=item['egg_id'])
            EggSale.objects.create(
                egg=egg,
                price=item['price'],
                invoice_number=invoice_number
            )
            egg.status = "sold"
            egg.save()

        messages.success(request, "Egg sale completed successfully!")
        return redirect('sales_list')

    return render(request, 'sales/egg_sale_review.html', {'egg_sale_pairs': egg_sale_pairs})

from django.http import HttpResponse, Http404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404
from .models import EggSale

def generate_egg_invoice(request, sale_id):
    # Ensure the EggSale record exists, or return 404
    sale = get_object_or_404(EggSale, id=sale_id)

    if not sale:
        raise Http404("Egg sale not found.")

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{sale.invoice_number}.pdf"'

    try:
        pdf = canvas.Canvas(response, pagesize=A4)
        pdf.setTitle(f"Invoice {sale.invoice_number}")

        # Invoice Title
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(200, 800, f"Invoice - {sale.invoice_number}")

        # Sale Details
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 750, f"Sale Date: {sale.sale_date}")
        pdf.drawString(100, 720, f"Egg Code: {sale.egg.egg_code}")
        pdf.drawString(100, 690, f"Price: {sale.price} L.E")

        # Footer
        pdf.line(100, 660, 500, 660)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, 640, f"Total: {sale.price} L.E")

        pdf.showPage()
        pdf.save()

        return response

    except Exception as e:
        return HttpResponse(f"Error generating invoice: {e}", status=500)

from django.http import HttpResponse, Http404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404
from .models import ChickSale

def generate_chick_invoice(request, sale_id):
    # Ensure the ChickSale record exists, or return 404
    sale = get_object_or_404(ChickSale, id=sale_id)

    if not sale:
        raise Http404("Chick sale not found.")

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{sale.invoice_number}.pdf"'

    try:
        pdf = canvas.Canvas(response, pagesize=A4)
        pdf.setTitle(f"Invoice {sale.invoice_number}")

        # Invoice Title
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(200, 800, f"Invoice - {sale.invoice_number}")

        # Sale Details
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 750, f"Sale Date: {sale.sale_date}")
        pdf.drawString(100, 720, f"Chick Name: {sale.chick.name}")
        pdf.drawString(100, 690, f"Price: {sale.price} L.E")

        # Footer
        pdf.line(100, 660, 500, 660)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, 640, f"Total: {sale.price} L.E")

        pdf.showPage()
        pdf.save()

        return response

    except Exception as e:
        return HttpResponse(f"Error generating invoice: {e}", status=500)


from django.shortcuts import render
from django.db.models import Sum, Count
from django.http import HttpResponse
import csv
from .models import Ostrich, Chick, Egg, Sale, FoodInventory, Cost

def reports_page(request):
    report_type = request.GET.get('report_type', 'sales')  # Default to sales report
    context = {}

    if report_type == 'sales':
        context['sales'] = Sale.objects.select_related('egg', 'chick', 'ostrich').all().order_by('-sale_date')

    elif report_type == 'ostrich_population':
        context['ostriches'] = Ostrich.objects.all().order_by('-age')

    elif report_type == 'chicks':
        context['chicks'] = Chick.objects.all().order_by('-creation_date')

    elif report_type == 'egg_production':
        context['eggs'] = Egg.objects.all().order_by('-lay_date_time')

    elif report_type == 'food_inventory':
        context['food_inventory'] = FoodInventory.objects.all()

    elif report_type == 'costs':
        context['costs'] = Cost.objects.all()

    return render(request, 'reports/reports_page.html', {'report_type': report_type, **context})

def export_report_csv(request):
    report_type = request.GET.get('report_type', 'sales')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
    writer = csv.writer(response)

    print(f"Generating report for: {report_type}")  # Debugging output

    if report_type == "sales":
        writer.writerow(["Item", "Category", "Quantity", "Price", "Sale Date"])
        sales = Sale.objects.select_related('egg', 'chick', 'ostrich').all()
        print(f"Found {sales.count()} sales records")  # Debugging output

        for sale in sales:
            item_name = sale.egg.egg_code if sale.egg else (sale.chick.name if sale.chick else sale.ostrich.name)
            writer.writerow([item_name, sale.get_category_display(), sale.quantity, sale.total_price, sale.sale_date])

    elif report_type == "ostrich_population":
        writer.writerow(["Name", "Age", "Gender", "Status"])
        ostriches = Ostrich.objects.all()
        print(f"Found {ostriches.count()} ostriches")  # Debugging output

        for ostrich in ostriches:
            writer.writerow([ostrich.name, ostrich.age, ostrich.gender, ostrich.status])

    elif report_type == "chicks":
        writer.writerow(["Name", "Age (Months)", "Gender", "Status"])
        chicks = Chick.objects.all()
        print(f"Found {chicks.count()} chicks")  # Debugging output

        for chick in chicks:
            writer.writerow([chick.name, chick.age_in_months, chick.gender, chick.status])

    elif report_type == "egg_production":
        writer.writerow(["Egg Code", "Lay Date", "Mother", "Father", "Fertility Status"])
        eggs = Egg.objects.all()
        print(f"Found {eggs.count()} eggs")  # Debugging output

        for egg in eggs:
            writer.writerow([
                egg.egg_code, egg.lay_date_time, 
                egg.mother.name if egg.mother else "Unknown",
                egg.father.name if egg.father else "Unknown",
                egg.fertile
            ])

    elif report_type == "food_inventory":
        writer.writerow(["Last Updated", "Current Inventory (kg)", "Estimated Finish Date"])
        food_inventory = FoodInventory.objects.all()
        print(f"Found {food_inventory.count()} food records")  # Debugging output

        for food in food_inventory:
            writer.writerow([food.last_updated, food.current_inventory, food.estimated_finish_date()])

    elif report_type == "costs":
        writer.writerow(["Name", "Price", "Category", "Date Paid", "Notes"])
        costs = Cost.objects.all()
        print(f"Found {costs.count()} costs")  # Debugging output

        for cost in costs:
            writer.writerow([cost.name, cost.price, cost.category.name, cost.date_paid, cost.notes])

    return response

import matplotlib.pyplot as plt
import io
import base64
import datetime
from django.shortcuts import render
from django.db.models import Count, Sum
from .models import Sale

def insights(request):
    # Define available KPIs (Y-axis)
    kpi_choices = {
        'total_sales': 'Total Sales Amount',
        'total_ostriches': 'Total Ostriches Sold',
        'total_chicks': 'Total Chicks Sold',
        'total_eggs': 'Total Eggs Sold',
    }

    # Get user-selected KPI
    y_axis_kpi = request.GET.get('y_axis_kpi', 'total_sales')

    # Get time range from user input (default to last 30 days)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=30)
    else:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    # Aggregate data by day, week, or month
    time_grouping = request.GET.get('time_grouping', 'daily')  # Default: Daily

    if time_grouping == 'daily':
        date_format = "%%Y-%%m-%%d"  # YYYY-MM-DD (Escape `%` for Django)
    elif time_grouping == 'weekly':
        date_format = "%%Y-%%W"  # YYYY-WeekNumber (Escape `%`)
    elif time_grouping == 'monthly':
        date_format = "%%Y-%%m"  # YYYY-MM (Escape `%`)
    else:
        date_format = "%%Y-%%m-%%d"  # Default to daily

    # Get user-selected chart type (default: Line Chart)
    chart_type = request.GET.get('chart_type', 'line')

    # Fetch sales data grouped by time
    sales_data = Sale.objects.filter(sale_date__range=[start_date, end_date]) \
        .extra(select={'time_period': f"strftime('{date_format}', sale_date)"}) \
        .values('time_period') \
        .annotate(
            total_sales=Sum('total_price'),
            total_ostriches=Count('ostrich'),
            total_chicks=Count('chick'),
            total_eggs=Count('egg')
        ).order_by('time_period')

    # Extract X and Y data
    x_values = [entry['time_period'] for entry in sales_data]
    y_values = [entry[y_axis_kpi] for entry in sales_data]

    # Generate chart based on user selection
    plt.figure(figsize=(8, 5))

    if chart_type == 'line':
        plt.plot(x_values, y_values, marker='o', linestyle='-', color='b')
    elif chart_type == 'bar':
        plt.bar(x_values, y_values, color='g')
    elif chart_type == 'pie':
        plt.pie(y_values, labels=x_values, autopct='%1.1f%%', startangle=90)
    elif chart_type == 'scatter':
        plt.scatter(x_values, y_values, color='r')
    elif chart_type == 'histogram':
        plt.hist(y_values, bins=10, color='purple', edgecolor='black')

    plt.xlabel("Time")
    plt.ylabel(kpi_choices[y_axis_kpi])
    plt.title(f"{kpi_choices[y_axis_kpi]} Over Time")

    # Convert plot to image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    chart_url = "data:image/png;base64," + base64.b64encode(image_png).decode()

    return render(request, 'reports/insights.html', {
        'chart_url': chart_url,
        'y_axis_kpi': y_axis_kpi,
        'kpi_choices': kpi_choices,
        'start_date': start_date,
        'end_date': end_date,
        'time_grouping': time_grouping,
        'chart_type': chart_type
    })





