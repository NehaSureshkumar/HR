from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0008_editaccessrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bank_account_number',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bank_ifsc',
            field=models.CharField(blank=True, max_length=20),
        ),
    ] 