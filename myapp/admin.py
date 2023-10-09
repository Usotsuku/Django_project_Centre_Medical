from django.contrib import admin
from .models import User,Medecin,Infirmiere,Salle,Patient,RendezVous,Materiel,Rh,UsageHistory
# Register your models here.
admin.site.register(User)
admin.site.register(Medecin)
admin.site.register(Infirmiere)
admin.site.register(Salle)
admin.site.register(Patient)
admin.site.register(RendezVous)
admin.site.register(Materiel)
admin.site.register(Rh)
admin.site.register(UsageHistory)