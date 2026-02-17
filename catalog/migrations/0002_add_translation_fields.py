from django.db import migrations, models


def copy_existing_text_to_translation_fields(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')
    Product = apps.get_model('catalog', 'Product')

    for category in Category.objects.all():
        updates = []
        if not category.name_en:
            category.name_en = category.name
            updates.append('name_en')
        if not category.name_ar:
            category.name_ar = category.name
            updates.append('name_ar')
        if updates:
            category.save(update_fields=updates)

    for product in Product.objects.all():
        updates = []
        if not product.name_en:
            product.name_en = product.name
            updates.append('name_en')
        if not product.name_ar:
            product.name_ar = product.name
            updates.append('name_ar')
        if not product.description_en:
            product.description_en = product.description
            updates.append('description_en')
        if not product.description_ar:
            product.description_ar = product.description
            updates.append('description_ar')
        if updates:
            product.save(update_fields=updates)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name_ar',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='name_en',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='description_ar',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='description_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='name_ar',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='name_en',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.RunPython(copy_existing_text_to_translation_fields, migrations.RunPython.noop),
    ]