from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from decimal import Decimal
import math
from django.db.models import Sum

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

    existance_choices = (
        ('exists','exists'),
        ('sold', 'sold'),
        ('slaughtered','Slaughtered')
    )
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='ostriches')
    name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length= 100, choices = gender_choices, null=True)
    status = models.CharField(max_length= 100, default="exists",choices = existance_choices, null=True)


    def __str__(self):
        return self.name

class Egg(models.Model):

    sale_choices = (
        ('exists','exists'),
        ('sold','sold')        
    )
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
    status = models.CharField(max_length= 100, default="exists",choices = sale_choices, null=True)

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
    

class Chick(models.Model):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female')
    ]
    sale_choices = (
        ('exists','exists'),
        ('sold','sold'),
    )
    name = models.CharField(max_length=100)
    creation_date = models.DateField(default=timezone.now)  # Date when the chick was created
    initial_age_in_months = models.PositiveIntegerField(null=True, blank=True)  # Optional for externally purchased chicks
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    pitch = models.ForeignKey('Pitch', on_delete=models.PROTECT, related_name='chicks', null=True, blank=True)
    status = models.CharField(max_length= 100,default="exists", choices = sale_choices, null=True)

    def __str__(self):
        return self.name

    @property
    def age_in_months(self):
        """Calculate the chick's age in months."""
        if self.initial_age_in_months is not None:
            # Use the initial age for externally purchased chicks
            return self.initial_age_in_months + self._calculate_dynamic_age()
        else:
            # Dynamically calculate age for chicks hatched from eggs
            return self._calculate_dynamic_age()

    def _calculate_dynamic_age(self):
        """Helper method to calculate dynamic age."""
        if not self.creation_date:
            return 0

        today = timezone.now().date()
        age_days = (today - self.creation_date).days
        return age_days // 30  # Approximate months (30 days per month)

    @property
    def eats_like_adult(self):
        """Check if the chick eats like an adult ostrich."""
        return self.age_in_months >= 2

    def total_adult_chicks():
        """Return the number of chicks that eat like adults."""
        today = timezone.now().date()
        two_months_ago = today - timezone.timedelta(days=60)

        # Filter chicks created more than 2 months ago or with initial_age_in_months >= 2
        adult_chicks = Chick.objects.filter(
            models.Q(creation_date__lte=two_months_ago, initial_age_in_months__isnull=True) |  # Chicks hatched from eggs
            models.Q(initial_age_in_months__gte=2)  # Externally purchased chicks
        )
        return adult_chicks.count()

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
        # Calculate total food inventory from purchases
        total_inventory = FoodPurchase.total_inventory()

        # Calculate daily consumption
        ostrich_count = Ostrich.objects.count()
        adult_chick_count = sum(1 for chick in Chick.objects.all() if chick.eats_like_adult)

        daily_consumption = (ostrich_count + adult_chick_count) * 2  # 2 kg per ostrich/chick per day

        try:
            # Try to get the existing FoodInventory object
            food_inventory = FoodInventory.objects.get(id=1)
            days_since_last_update = (timezone.now().date() - food_inventory.last_updated.date()).days
        except FoodInventory.DoesNotExist:
            # If it doesn't exist, create a new one
            food_inventory = FoodInventory.objects.create(id=1, current_inventory=total_inventory)
            days_since_last_update = 0

        # Ensure days_since_last_update is an integer
        days_since_last_update = max(days_since_last_update, 0)

        # Update the current inventory
        total_daily_consumption = Decimal(daily_consumption) * days_since_last_update
        current_inventory = max(Decimal(total_inventory or 0) - total_daily_consumption, 0)
        food_inventory.current_inventory = current_inventory
        food_inventory.save()

    @staticmethod
    def estimated_finish_date():        # Estimate when the food will run out
        ostrich_count = Ostrich.objects.count()
        adult_chick_count = Chick.total_adult_chicks()  # Use the updated method
        if ostrich_count + adult_chick_count == 0:
            return "No ostriches or chicks in the farm."

        daily_consumption = (ostrich_count + adult_chick_count) * 2  # 2 kg per ostrich/chick per day
        try:
            food_inventory = FoodInventory.objects.get(id=1)
            current_inventory = food_inventory.current_inventory
        except FoodInventory.DoesNotExist:
            current_inventory = 0

        if daily_consumption == 0 or current_inventory == 0:
            return "No ostriches or chicks or no food available."

        # Calculate days left as an integer
        days_left = math.ceil(Decimal(current_inventory) / Decimal(daily_consumption))
        finish_date = timezone.now().date() + timezone.timedelta(days=days_left)
        return finish_date

class CostCategory(models.Model):
    """Model to store cost categories."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Cost(models.Model):
    """Model to store individual costs."""
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(CostCategory, on_delete=models.PROTECT, related_name='costs')
    date_paid = models.DateField(default=timezone.now, null=True, blank=True)  # For periodic costs
    notes = models.TextField(blank=True, null=True)  # Optional notes field

    def __str__(self):
        return f"{self.name} - {self.price} ({self.category})"
    