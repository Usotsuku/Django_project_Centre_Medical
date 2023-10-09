
from django.urls import path,include
from . import views
from .views import CustomLogoutView

urlpatterns = [
    path('', views.redirect_home, name='redirect_home'),
    path('home/', views.home, name='home'),
    path('mod', views.mod, name='mod'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('rh/', views.rh, name='rh'),
    path('visiteur/', views.visiteur, name='visiteur'),
    path('infermiere/', views.infermiere, name='infermiere'),
    path('medecin/', views.medecin, name='medecin'),
    path('modify/<int:id>/', views.modify_user, name='modify_user'),
    path('delete/<int:id>/', views.delete_user, name='delete_user'),
    path('change_password/<int:id>/', views.change_user_password, name='change_password'),
    path('consulter-patients/', views.consulter_patients, name='consulter_patients'),
    path('demander-reservation/', views.demander_reservation, name='demander_reservation'),
    path('afficher-calendrier/', views.afficher_calendrier, name='afficher_calendrier'),
    path('modifier-informations/', views.modifier_informations, name='modifier_informations'),
    path('patients/', views.patients_list, name='patients_list'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/<int:id>/update/', views.update_patient, name='update_patient'),
    path('patients/<int:id>/delete/', views.confirm_delete_patient, name='delete_patient'),
    path('select_date/<int:patient_id>/', views.select_date, name='select_date'),
    path('rendezvous_list/', views.rendezvous_list, name='rendezvous_list'),
    path('modify_rendezvous/<int:rendezvous_id>/', views.modify_rendezvous, name='modify_rendezvous'),
    path('rendezvous/<int:rendezvous_id>/delete/', views.delete_rendezvous, name='delete_rendezvous'),
    path('salle_list/', views.salle_list, name='salle_list'),
    path('salle/<int:salle_id>/reserver', views.reserver_salle, name='reserver_salle'),
    path('salle/<int:salle_id>/liberer', views.liberer_salle, name='liberer_salle'),
    path('materiels/', views.materiels_list, name='materiels_list'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('patientrendezvous/', views.patient_rendezvous, name='patient_rendezvous'),
    path('search/', views.search_users, name='search_users'),
]
