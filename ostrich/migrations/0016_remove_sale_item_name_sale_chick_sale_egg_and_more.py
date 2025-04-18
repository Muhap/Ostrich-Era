# Generated by Django 5.1.6 on 2025-03-15 01:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ostrich', '0015_sale'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='item_name',
        ),
        migrations.AddField(
            model_name='sale',
            name='chick',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ostrich.chick'),
        ),
        migrations.AddField(
            model_name='sale',
            name='egg',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ostrich.egg'),
        ),
        migrations.AddField(
            model_name='sale',
            name='ostrich',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ostrich.ostrich'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='category',
            field=models.CharField(choices=[('egg', 'Unfertile Egg'), ('chick', 'Chick'), ('ostrich', 'Ostrich')], max_length=10),
        ),
        migrations.AlterField(
            model_name='sale',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
