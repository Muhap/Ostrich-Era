from django import forms
from .models import Egg, Ostrich, FoodPurchase

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