# Generated by Django 4.1.7 on 2024-09-05 00:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Caisse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_deb', models.DateField()),
                ('date_fin', models.DateField()),
                ('montant_caisse', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Membre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_membre', models.CharField(max_length=100)),
                ('prenom_membre', models.CharField(max_length=100)),
                ('activite_membre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Reunion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_reunion', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Verser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_versement', models.DateField()),
                ('montant_verser', models.FloatField()),
                ('membre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Micro.membre')),
            ],
        ),
        migrations.CreateModel(
            name='Tampon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_deb', models.DateField()),
                ('date_fin', models.DateField()),
                ('nb_tampon', models.IntegerField()),
                ('membre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Micro.membre')),
            ],
        ),
        migrations.CreateModel(
            name='Pret',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_pret', models.DateField()),
                ('date_rembourser', models.DateField()),
                ('montant_pret', models.FloatField()),
                ('montant_rembouresser', models.FloatField()),
                ('caisse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Micro.caisse')),
                ('membre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Micro.membre')),
            ],
        ),
        migrations.CreateModel(
            name='MontantMbr',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant_mbr', models.FloatField()),
                ('membre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Micro.membre')),
            ],
        ),
        migrations.CreateModel(
            name='Assist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assister', models.BooleanField(default=False)),
                ('penalite', models.BooleanField(default=False)),
                ('membre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Micro.membre')),
                ('reunion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Micro.reunion')),
            ],
        ),
    ]
