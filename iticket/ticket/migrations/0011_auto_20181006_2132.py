# Generated by Django 2.1.1 on 2018-10-06 18:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0010_auto_20181006_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickethistory',
            name='ticket',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='history', to='ticket.Ticket', verbose_name='Тикет'),
        ),
    ]
