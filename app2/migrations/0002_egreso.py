# Generated by Django 5.0.6 on 2024-06-13 04:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Egreso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_pedido', models.DateField(max_length=255)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('pagado', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('comentarios', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('ticket', models.BooleanField(default=True)),
                ('desglosar', models.BooleanField(default=True)),
                ('updated', models.DateTimeField(auto_now_add=True, null=True)),
                ('cliente', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clientee', to='app2.cliente')),
            ],
            options={
                'verbose_name': 'egreso',
                'verbose_name_plural': 'egresos',
                'order_with_respect_to': 'fecha_pedido',
            },
        ),
    ]