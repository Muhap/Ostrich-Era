from django import forms
from .models import Egg, Ostrich, FoodPurchase, Chick , CostCategory, Cost

class EggForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EggForm, self).__init__(*args, **kwargs)
        # Filter male ostriches for the father field
        self.fields['father'].queryset = Ostrich.objects.filter(gender='male')
        # Filter female ostriches for the mother field
        self.fields['mother'].queryset = Ostrich.objects.filter(gender='female')

    class Meta:
        model = Egg
        fields = ['egg_code', 'lay_date_time', 'mother', 'father', 'weight']

class FoodPurchaseForm(forms.ModelForm):
    class Meta:
        model = FoodPurchase
        fields = ['purchase_date', 'quantity_kg', 'price_per_kg']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'quantity_kg': forms.NumberInput(attrs={'step': '0.01'}),
            'price_per_kg': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ChickFromEggForm(forms.ModelForm):
    class Meta:
        model = Chick
        fields = ['name', 'gender', 'pitch']  # No age_in_months field

class ChickFromOutsideForm(forms.ModelForm):
    class Meta:
        model = Chick
        fields = ['name', 'initial_age_in_months', 'gender', 'pitch']
        widgets = {
            'initial_age_in_months': forms.NumberInput(attrs={'min': 0}),
        }

class CostForm(forms.ModelForm):
    class Meta:
        model = Cost
        fields = ['name', 'price', 'date_paid', 'notes']  
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'date_paid': forms.DateInput(attrs={'type': 'date'}),
        }

from django import forms
from .models import Sale
from django.contrib import messages

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['category', 'egg', 'chick', 'ostrich', 'quantity', 'price_per_unit', 'sale_date']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)  # Get request object if passed
        super().__init__(*args, **kwargs)

        available_eggs = Egg.objects.filter(status='exists')
        available_chicks = Chick.objects.filter(status='exists')
        available_ostriches = Ostrich.objects.filter(status='exists')

        self.fields['egg'].queryset = available_eggs
        self.fields['chick'].queryset = available_chicks
        self.fields['ostrich'].queryset = available_ostriches

        if request:
            if not available_eggs.exists():
                messages.warning(request, "No available eggs for sale.")
            if not available_chicks.exists():
                messages.warning(request, "No available chicks for sale.")
            if not available_ostriches.exists():
                messages.warning(request, "No available ostriches for sale.")

        self.fields['egg'].required = False
        self.fields['chick'].required = False
        self.fields['ostrich'].required = False
        
class OstrichSelectionForm(forms.Form):
    ostriches = forms.ModelMultipleChoiceField(
        queryset=Ostrich.objects.filter(status='exists'),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

class OstrichSaleForm(forms.Form):
    weight_kg = forms.DecimalField(max_digits=6, decimal_places=2, label="Weight (kg)")
    price = forms.DecimalField(max_digits=10, decimal_places=2, label="Sale Price")

class ChickSelectionForm(forms.Form):
    chicks = forms.ModelMultipleChoiceField(
        queryset=Chick.objects.filter(status='exists'),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

class ChickSaleForm(forms.Form):
    price = forms.DecimalField(max_digits=10, decimal_places=2, label="Sale Price")

class EggSelectionForm(forms.Form):
    eggs = forms.ModelMultipleChoiceField(
        queryset=Egg.objects.filter(fertile="Not Fertile", status='exists'),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
