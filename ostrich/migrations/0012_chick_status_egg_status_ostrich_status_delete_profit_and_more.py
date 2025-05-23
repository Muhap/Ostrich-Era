# Generated by Django 5.1.6 on 2025-03-14 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ostrich', '0011_profitcategory_remove_customuser_groups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chick',
            name='status',
            field=models.CharField(choices=[('exists', 'exists'), ('sold', 'sold')], default='exists', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='egg',
            name='status',
            field=models.CharField(choices=[('exists', 'exists'), ('sold', 'sold')], default='exists', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='ostrich',
            name='status',
            field=models.CharField(choices=[('exists', 'exists'), ('sold', 'sold'), ('slaughtered', 'Slaughtered')], default='exists', max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='Profit',
        ),
        migrations.DeleteModel(
            name='ProfitCategory',
        ),
    ]
