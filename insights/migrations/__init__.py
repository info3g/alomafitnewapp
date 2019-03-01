# Generated by Django 2.0 on 2018-09-14 17:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HitProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=255, unique=True)),
                ('try_duration_seconds', models.IntegerField(default=60)),
            ],
            options={
                'ordering': ('product', 'try_duration_seconds', 'token'),
            },
        ),
        migrations.CreateModel(
            name='Product_Profile_Add_To_Closet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'ordering': ('product',),
            },
        ),
        migrations.CreateModel(
            name='Profile_Try_Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('try_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('product', 'profile'),
            },
        ),
        migrations.CreateModel(
            name='Profile_Visit_Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_visiting', to='customers.Profile')),
            ],
            options={
                'ordering': ('store', 'profile'),
            },
        ),
    ]
