from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from decimal import Decimal

class Pitch(models.Model):
    pitch_number = models.IntegerField(unique=True)

    def __str__(self):
        return f"Pitch {self.pitch_number}"
     
    @property
    def number_of_families(self):
        # Use the related_name 'families' to count the families in this pitch
        return self.families.count()

class Family(models.Model):
    Family_name = models.CharField(max_length=100, null=True)
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE, related_name='families')

    def __str__(self):
        if self.Family_name :
            return f"{self.Family_name} in {self.pitch}"
        else:
            return f"Family in {self.pitch}"

class Ostrich(models.Model):
    gender_choices= (
        ('male','male'),
        ('female','female')
    )
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='ostriches')
    name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length= 100, choices = gender_choices, null=True)

    def __str__(self):
        return self.name

class Egg(models.Model):
    egg_code = models.CharField(max_length=50, unique=True)
    lay_date_time = models.DateTimeField(default=timezone.now)
    mother = models.ForeignKey('Ostrich', on_delete=models.PROTECT, related_name='eggs_laid', null=True, blank=True)
    father = models.ForeignKey('Ostrich', on_delete=models.PROTECT, related_name='eggs_fathered', null=True, blank=True)
    fertile = models.CharField(
        max_length=20,
        default='Waiting First Check',
        choices=[
            ('Waiting First Check', 'Waiting First Check'),
            ('Fertile', 'Fertile'),
            ('Not Fertile', 'Not Fertile')
        ]
    )
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    batch = models.ForeignKey('Batch', on_delete=models.SET_NULL, null=True, blank=True, related_name='eggs')

    def __str__(self):
        return self.egg_code
    
class Batch(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    first_check_date = models.DateTimeField(blank=True, null=True)
    finish_date = models.DateTimeField(blank=True, null=True)
    batch_code = models.CharField(max_length=100, unique=True, blank=True)

    @property
    def status(self):
        now = timezone.now()
        if now < self.first_check_date:
            return "Starting"
        elif self.first_check_date <= now < self.finish_date:
            return "First Check Done"
        else:
            return "Finished"

    @property
    def number_of_eggs(self):
        return self.eggs.count()

    def save(self, *args, **kwargs):
        # Automatically calculate first_check_date and finish_date
        if not self.first_check_date:
            self.first_check_date = self.creation_date + timedelta(days=15)
        if not self.finish_date:
            self.finish_date = self.creation_date + timedelta(days=39)

        # Generate batch_code
        if not self.batch_code:
            # Use 'temp' as a placeholder for the ID until the object is saved
            temp_id = 'temp'
            creation_date_str = self.creation_date.strftime('%d/%m/%Y')
            finish_date_str = self.finish_date.strftime('%d/%m/%Y')
            self.batch_code = f"Batch {temp_id} [{creation_date_str} - {finish_date_str}]"

        super().save(*args, **kwargs)  # Save the object to get the actual ID

        # Update batch_code with the actual ID after saving
        if self.batch_code.startswith('Batch temp'):
            creation_date_str = self.creation_date.strftime('%d/%m/%Y')
            finish_date_str = self.finish_date.strftime('%d/%m/%Y')
            self.batch_code = f"Batch {self.id} [{creation_date_str} - {finish_date_str}]"
            self.save()  # Save again to update the batch_code

    def __str__(self):
        return self.batch_code
    
import math
from django.db import models
from django.utils import timezone
from django.db.models import Sum

class FoodPurchase(models.Model):
    purchase_date = models.DateField(default=timezone.now)
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity_kg} kg purchased on {self.purchase_date}"

    @staticmethod
    def total_inventory():
        # Calculate the total food inventory from all purchases
        total_quantity = FoodPurchase.objects.aggregate(Sum('quantity_kg'))['quantity_kg__sum']
        return total_quantity if total_quantity else 0

class FoodInventory(models.Model):
    last_updated = models.DateTimeField(auto_now=True)
    current_inventory = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @staticmethod
    def update_inventory():
        # Calculate the total food inventory from all purchases
        total_inventory = FoodPurchase.total_inventory()
        ostrich_count = Ostrich.objects.count()
        daily_consumption = ostrich_count * 2  # 2 kg per ostrich per day

        try:
            # Try to get the existing FoodInventory object
            food_inventory = FoodInventory.objects.get(id=1)
            days_since_last_update = (timezone.now().date() - food_inventory.last_updated.date()).days
        except FoodInventory.DoesNotExist:
            # If it doesn't exist, create a new one
            food_inventory = FoodInventory.objects.create(id=1, current_inventory=total_inventory)
            days_since_last_update = 0

        # Ensure days_since_last_update is an integer
        days_since_last_update = max(days_since_last_update, 0)  # Prevent negative days

        # Convert daily consumption to Decimal for precise calculations
        total_daily_consumption = Decimal(daily_consumption) * days_since_last_update

        # Update the current inventory
        current_inventory = max(total_inventory - total_daily_consumption, 0)
        food_inventory.current_inventory = current_inventory
        food_inventory.save()

    @staticmethod
    @staticmethod
    def estimated_finish_date():
        ostrich_count = Ostrich.objects.count()
        if ostrich_count == 0:
            return "No ostriches in the farm."

        daily_consumption = ostrich_count * 2  # 2 kg per ostrich per day
        try:
            food_inventory = FoodInventory.objects.get(id=1)
            current_inventory = food_inventory.current_inventory
        except FoodInventory.DoesNotExist:
            current_inventory = 0

        if daily_consumption == 0 or current_inventory == 0:
            return "No ostriches or no food available."

        # Calculate days left as an integer
        days_left = math.ceil(current_inventory / daily_consumption)  # Round up to ensure food lasts until the end of the day
        finish_date = timezone.now().date() + timezone.timedelta(days=days_left)
        return finish_date