# Remove field loaded from fixture

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("salesforce", "0015_sobjectfield_filterable"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                # delete the intermediate entries
                "DELETE FROM slack_formfield where field_id='77f62583-c26f-4ba0-91c4-238f97531a8f';",
                # delete the meeting_sentiment field
                "DELETE FROM salesforce_sobjectfield where id='77f62583-c26f-4ba0-91c4-238f97531a8f';",
            ]
        )
    ]
