from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queue_board', '0003_alter_patient_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='phone_number',
            field=models.CharField(blank=True, db_index=True, max_length=15, null=True, unique=True),
        ),
    ]
