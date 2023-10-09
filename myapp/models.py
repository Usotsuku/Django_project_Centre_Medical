from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_rh= models.BooleanField('Is rh', default=False)
    is_medecin = models.BooleanField('Is medecin', default=False)
    is_infermiere = models.BooleanField('Is infermiere', default=False)
    is_visiteur = models.BooleanField('Is visiteur', default=False)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)

class Medecin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialite = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.username}"

class Infirmiere(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_embauche_inf= models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"

class Rh(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_embauche_rh = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    raison_de_visite = models.TextField()
    medecin_traitant = models.ForeignKey(Medecin, on_delete=models.SET_NULL, null=True,related_name="patients")

    def __str__(self):
        return f"{self.user.username}"

class Salle(models.Model):
    type_salle = models.CharField(max_length=100)
    est_occupee = models.BooleanField(default=False)
    occuppee_par = models.ForeignKey(Medecin, on_delete=models.SET_NULL, null=True, blank=True)

class UsageHistory(models.Model):
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE)
    date_used = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    
class RendezVous(models.Model):
    date_heure = models.DateTimeField()
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

class Materiel(models.Model):
    nom = models.CharField(max_length=100)
    derniere_maintenance = models.DateField()