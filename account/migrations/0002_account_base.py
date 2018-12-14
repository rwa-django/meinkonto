# Generated by Django 2.1.3 on 2018-12-14 21:09

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account_Base',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('account_info', models.CharField(help_text='Buchungs Info', max_length=200)),
                ('account_start_day', models.PositiveSmallIntegerField(default=0, help_text='Format: <MM>', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)])),
                ('account_type', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='account.Account_Type')),
                ('login', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]