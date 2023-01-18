# Generated by Django 4.1.5 on 2023-01-16 21:54

import datetime
from django.db import migrations, models
import django.db.models.deletion
import routing.fields


class Migration(migrations.Migration):

    dependencies = [
        ('routing', '0002_alter_emergency_timestamp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emergency',
            name='lat',
            field=models.DecimalField(decimal_places=15, max_digits=17),
        ),
        migrations.AlterField(
            model_name='emergency',
            name='long',
            field=models.DecimalField(decimal_places=15, max_digits=17),
        ),
        migrations.AlterField(
            model_name='emergency',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 16, 21, 54, 8, 700748, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='emergencyvehicle',
            name='call_name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='emergencyvehicle',
            name='last_ping',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 16, 21, 54, 8, 700748, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='emergencyvehicle',
            name='lat',
            field=models.DecimalField(decimal_places=15, max_digits=17),
        ),
        migrations.AlterField(
            model_name='emergencyvehicle',
            name='long',
            field=models.DecimalField(decimal_places=15, max_digits=17),
        ),
        migrations.CreateModel(
            name='RouteRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nodes', routing.fields.IntegerListField(max_length=2000)),
                ('start_linestring', models.CharField(max_length=1000)),
                ('end_linestring', models.CharField(max_length=1000)),
                ('weight', models.FloatField()),
                ('length', models.FloatField()),
                ('emergency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='routing.emergency')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='routing.emergencyvehicle')),
            ],
        ),
    ]