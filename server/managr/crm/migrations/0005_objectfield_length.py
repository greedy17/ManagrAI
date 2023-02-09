from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0004_auto_20221010_2032"),
    ]

    operations = [
        migrations.AddField(
            model_name="objectfield", name="length", field=models.PositiveIntegerField(default=0),
        ),
    ]
