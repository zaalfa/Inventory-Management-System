from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'categories', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('stock', models.IntegerField(default=0)),
                ('min_stock', models.IntegerField(default=5)),
                ('sku', models.CharField(blank=True, max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('is_active', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='products', to='products.category'
                )),
            ],
            options={'db_table': 'products', 'ordering': ['name']},
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['sku'], name='products_sku_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category'], name='products_category_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_active'], name='products_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['stock'], name='products_stock_idx'),
        ),
    ]
