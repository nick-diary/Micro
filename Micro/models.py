from django.db import models


class Membre(models.Model):
    nom_membre = models.CharField(max_length=100)
    prenom_membre = models.CharField(max_length=100)
    activite_membre = models.CharField(max_length=100)


class Verser(models.Model):
    date_versement = models.DateField()
    montant_verser = models.IntegerField()
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)

class Semaine(models.Model):
    date_deb = models.DateField()
    date_fin = models.DateField()

class Tampon(models.Model):
    nb_tampon = models.IntegerField()
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    semaine = models.ForeignKey(Semaine, on_delete=models.CASCADE, default=1)


class Caisse(models.Model):
    date_deb = models.DateField()
    date_fin = models.DateField()
    montant_caisse = models.FloatField()


class Pret(models.Model):
    date_pret = models.DateField()
    # date_rembourser = models.DateField()
    montant_pret = models.FloatField()
    montant_paye = models.FloatField(default=0)
    etat_pret = models.BooleanField(default=False)
    montant_rembouresser = models.FloatField()
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    caisse = models.ForeignKey(Caisse, on_delete=models.CASCADE)

class Remboursement(models.Model):
    id_membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    id_pret = models.ForeignKey(Pret, on_delete=models.CASCADE)
    date_rembours = models.DateField()
    montant_rembours = models.FloatField()
    reste_paye =models.FloatField()
#     date_remboursement = models.DateField()
#     montant_interet = models.FloatField()
#     montant_rembouresser = models.FloatField()
#     membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
#     pret = models.ForeignKey(Pret, on_delete=models.CASCADE)

class Reunion(models.Model):
    date_reunion = models.DateTimeField()    

    def get_attendance_count(self):
        return self.assist_set.filter(assister=True).count()

    def get_total_membres(self):
        # return Membre.objects.count()
        return self.assist_set.values('membre').distinct().count()


class Assist(models.Model):
    assister = models.BooleanField(default=False)
    penalite = models.BooleanField(default=False)
    reunion = models.ForeignKey(Reunion, on_delete=models.CASCADE)
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)

class MontantMbr(models.Model):
    montant_mbr = models.FloatField()
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)

class Rembourser(models.Model):
    id_membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    id_pret = models.ForeignKey(Pret, on_delete=models.CASCADE)
    date_rembours = models.DateField()
    montant_rembours = models.FloatField()
    reste_paye =models.FloatField()