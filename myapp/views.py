
from .forms import SignUpForm, LoginForm,PatientForm,SelectDateForm,AddPatientForm
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import date,datetime, timedelta
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from .models import User,Materiel,UsageHistory, Infirmiere, Rh, Patient, Medecin,RendezVous,Salle

@login_required
def redirect_home(request):
    if request.user.is_rh:
        return redirect('rh')
    elif request.user.is_medecin:
        return redirect('medecin')
    elif request.user.is_infermiere:
        return redirect('infermiere')
    elif request.user.is_visiteur:
        return redirect('visiteur')
    elif request.user.is_staff:
        return redirect('mod')
    else:
        return redirect('home')

def home(request):
    return render(request,'home.html')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login') 

def is_medecin(user):
    return user.is_authenticated and (user.is_medecin or user.is_staff)

def is_infermiere(user):
    return user.is_authenticated and (user.is_infermiere or user.is_staff)

def is_infermiere_rh(user):
    return user.is_authenticated and (user.is_infermiere or user.is_staff or user.is_rh)

def is_visiteur(user):
    return user.is_authenticated and (user.is_visiteur or user.is_staff)

def is_rh(user):
    return user.is_authenticated and (user.is_rh or user.is_staff)

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def mod(request):
    user =  request.user
    if user is not None and user.is_staff:
        
        return render(request, 'admin.html',{'user':user})
    
@login_required
@user_passes_test(is_infermiere_rh)
def search_users(request):
    user =  request.user
    if user is not None and (user.is_rh or user.is_staff):
        query = request.GET.get('q')
        users = User.objects.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) 
        ).filter(is_superuser=False, is_staff=False)

        return render(request, 'rh.html', {'users': users})
    elif user is not None and (user.is_infermiere or user.is_staff):
        query = request.GET.get('q')
        patients = Patient.objects.filter(
            Q(user__nom__icontains=query) |
            Q(user__prenom__icontains=query)
        )

        return render(request, 'patients.html', {'patients': patients})

def register(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                nom=form.cleaned_data['nom'],
                prenom=form.cleaned_data['prenom'],
                is_medecin = form.cleaned_data['is_medecin'],
                is_rh = form.cleaned_data['is_rh'],
                is_infermiere = form.cleaned_data['is_infermiere'],
                is_visiteur = form.cleaned_data['is_visiteur'],
                is_staff=form.cleaned_data['is_admin'], 
            )
            if form.cleaned_data['is_medecin']:
                medecin = Medecin.objects.create(
                    user=user,
                    specialite='',
                )
            elif form.cleaned_data['is_infermiere']:
                infirmiere = Infirmiere.objects.create(
                    user=user,
                    date_embauche_inf='',
                )
            elif form.cleaned_data['is_visiteur']:
                patient = Patient.objects.create(
                    user=user,
                    raison_de_visite='',
                )
            elif form.cleaned_data['is_rh']:
                rh = Rh.objects.create(
                    user=user,
                    date_embauche_rh='',
                )
            msg = 'User created'
            return redirect('login')
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form, 'msg': msg})

def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if 'next' in request.GET:
        msg = "Vous n'avez pas la permission d'accéder à la page demandée."

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('mod')
                elif user.is_rh:
                    return redirect('rh')
                elif user.is_medecin:
                    return redirect('medecin')
                elif user.is_infermiere:
                    return redirect('infermiere')
                elif user.is_visiteur:
                    return redirect('visiteur')
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating form'

    return render(request, 'login.html', {'form': form, 'msg': msg})


@login_required
@user_passes_test(is_rh)
def rh(request):
    users = User.objects.filter(is_superuser=False , is_staff=False)
    return render(request, 'rh.html', {'users': users})

@login_required
@user_passes_test(is_rh)
def modify_user(request, id):
    user = User.objects.get(id=id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        
        is_rh = bool(request.POST.getlist('is_rh'))
        is_medecin = bool(request.POST.getlist('is_medecin'))
        is_infermiere = bool(request.POST.getlist('is_infermiere'))
        is_visiteur = bool(request.POST.getlist('is_visiteur'))

        user.username = username
        user.email = email
        user.is_rh = is_rh
        user.is_medecin = is_medecin
        user.is_infermiere = is_infermiere
        user.is_visiteur = is_visiteur
        user.nom = nom
        user.prenom = prenom
        user.save()

        return redirect('rh')
    else:
        return render(request, 'modify_user.html', {'user': user})

@login_required
@user_passes_test(is_rh)
def delete_user(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return redirect('rh')

@login_required
@user_passes_test(is_rh)
def change_user_password(request, id):
    user = User.objects.get(id=id)

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password was successfully updated')
            return redirect('rh')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user)
    return render(request, 'change_password.html', {'form': form})

@login_required
@user_passes_test(is_visiteur)
def visiteur(request):
    if request.method == 'POST':
        medecin_id = request.POST.get('medecin')
        date_heure_str = request.POST.get('date_heure')
        date_heure = datetime.strptime(date_heure_str, '%Y-%m-%dT%H:%M')

        medecin = Medecin.objects.get(id=medecin_id)
        patient = Patient.objects.get(user=request.user)
        raison_de_visite = request.POST.get('raison_de_visite')

        rendezvous = RendezVous.objects.create(
            medecin=medecin,
            patient=patient,
            date_heure=date_heure,
        )

        patient.medecin_traitant = medecin
        patient.raison_de_visite = raison_de_visite
        patient.save()

        return redirect('visiteur')

    else:
        medecins = Medecin.objects.all()
        return render(request, 'visiteur.html', {'medecins': medecins})

@login_required
@user_passes_test(is_visiteur)  
def patient_rendezvous(request):
    current_date = timezone.now()
    
    user_rendezvous = RendezVous.objects.filter(patient=request.user.patient)
    
    old_rendezvous = [r for r in user_rendezvous if r.date_heure < current_date]
    upcoming_rendezvous = [r for r in user_rendezvous if r.date_heure >= current_date]
    
    return render(request, 'patient_rendezvous.html', {
        'old_rendezvous': old_rendezvous,
        'upcoming_rendezvous': upcoming_rendezvous,
    })
    
@login_required
@user_passes_test(is_infermiere)  
def infermiere(request):
    infermiere =  Infirmiere.objects.get(user=request.user)
    return render(request,'infermiere.html',{'infermiere':infermiere})

@login_required
@user_passes_test(is_infermiere)
def patients_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients.html', {'patients': patients})

@login_required
@user_passes_test(is_infermiere)
def add_patient(request):
    if request.method == 'POST':
        form = AddPatientForm(request.POST)
        if form.is_valid():
            default_password = '00000000'
            user = User.objects.create(
                username=form.cleaned_data['prenom'],
                email=form.cleaned_data['email'],
                nom=form.cleaned_data['nom'],
                prenom=form.cleaned_data['prenom'],
                is_visiteur = True,
            )
            user.set_password(default_password)
            user.save()
            patient = Patient.objects.create(
                user=user,
                medecin_traitant=form.cleaned_data['medecin_traitant'],
                raison_de_visite=form.cleaned_data['raison_de_visite'],
            )
            
            return redirect('patients_list')
    else:
        form = AddPatientForm()
    
    return render(request, 'addpatient.html', {'form': form})

@login_required
@user_passes_test(is_infermiere)
def update_patient(request, id):
    patient = get_object_or_404(Patient, id=id)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patients_list')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'updatepatient.html', {'form': form})

def confirm_delete_patient(request, id):
    patient_instance = get_object_or_404(Patient, id=id)

    if request.method == 'POST':
        user = patient_instance.user  
        patient_instance.delete() 
        user.delete()  
        return redirect('patients_list') 

    return render(request, 'delete.html', {'patient': patient_instance})

@login_required
@user_passes_test(is_infermiere)
def rendezvous_list(request):
    current_date = datetime.now()
    rendezvous_list = RendezVous.objects.filter( date_heure__gte=current_date)
    return render(request, 'rendezvous_list.html', {'rendezvous_list': rendezvous_list})


@login_required
@user_passes_test(is_infermiere)
def select_date(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    doctor = patient.medecin_traitant

    if request.method == 'POST':
        form = SelectDateForm(request.POST)
        if form.is_valid():
           date_heure = form.cleaned_data['date_heure']
           RendezVous.objects.create(date_heure=date_heure, medecin=doctor, patient=patient)
           return redirect('rendezvous_list')
    else:
       form = SelectDateForm()
       form.fields['date_heure'].initial = timezone.localtime(timezone.now()).replace(hour=9, minute=0)
       form.fields['date_heure'].widget.attrs.update({'class': 'datetime-input'})

    return render(request, 'select_date.html', {'patient': patient, 'doctor': doctor, 'form': form})

@login_required
@user_passes_test(is_infermiere)
def modify_rendezvous(request, rendezvous_id):
    rendezvous = get_object_or_404(RendezVous, pk=rendezvous_id)
    if request.method == 'POST':
        form = SelectDateForm(request.POST)
        if form.is_valid():
            rendezvous.date_heure = form.cleaned_data['date_heure']
            rendezvous.save()
            return redirect('rendezvous_list')
    else:
        form = SelectDateForm(initial={'date_heure': rendezvous.date_heure})
    return render(request, 'modify_rendezvous.html', {'form': form, 'rendezvous': rendezvous})

@login_required
@user_passes_test(is_infermiere)
def delete_rendezvous(request, rendezvous_id):
    rendezvous = get_object_or_404(RendezVous, id=rendezvous_id)
    if request.method == 'POST':
        rendezvous.delete()
        return redirect('rendezvous_list')
    context = {'rendezvous': rendezvous}
    return render(request, 'delete_rendezvous.html', context)


@login_required
@user_passes_test(is_infermiere)
def salle_list(request):

    salles = Salle.objects.all()

    for salle in salles:
        if salle.occuppee_par:
            salle.est_occupee = True
        else:
            salle.est_occupee = False

    medecins = Medecin.objects.all()

    return render(request, 'salle_list.html', {'salles': salles, 'medecins': medecins})


@login_required
@user_passes_test(is_infermiere)
def reserver_salle(request, salle_id):
    salle = get_object_or_404(Salle, pk=salle_id)
    medecin_id = request.POST['medecin']
    medecin = get_object_or_404(Medecin, pk=medecin_id)
    salle.occuppee_par = medecin
    salle.est_occupee = True
    salle.save()
    return redirect('salle_list')

@login_required
@user_passes_test(is_infermiere)
def liberer_salle(request, salle_id):
    salle = get_object_or_404(Salle, pk=salle_id)
    salle.occuppee_par = None
    salle.est_occupee = False
    salle.save()
    return redirect('salle_list')


@login_required
@user_passes_test(is_infermiere)
def materiels_list(request):
    materials = Materiel.objects.all()
    today = date.today()

    for material in materials:
        # Calculate the difference between today and the last maintenance date
        maintenance_diff = today - material.derniere_maintenance
        if maintenance_diff.days > 15:
            material.status = "Besoin de maintenance"
        else:
            material.status = "OK"

    context = {
        'materials': materials
    }

    return render(request, 'materiels_list.html', context)

@login_required
@user_passes_test(is_medecin)
def medecin(request):
    current_medecin = Medecin.objects.get(user=request.user)
    return render(request,'medecin.html',{'medecin':current_medecin})

@login_required
@user_passes_test(is_medecin)
def consulter_patients(request):
    current_medecin = Medecin.objects.get(user=request.user)
    patients = Patient.objects.filter(medecin_traitant=current_medecin)
    return render(request, 'consulter_patients.html', {'patients': patients})


@login_required
@user_passes_test(is_medecin)
def demander_reservation(request):
    selected_salle = None
    if request.method == 'POST':
        salle_id = request.POST.get('salle_id')
        selected_salle = Salle.objects.get(pk=salle_id)
        
        if not selected_salle.est_occupee:
            current_medecin = Medecin.objects.get(user=request.user)
            
            selected_salle.est_occupee = True
            selected_salle.occuppee_par = current_medecin
            selected_salle.save()

            end_time_str = request.POST.get('end_time')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
            
            UsageHistory.objects.create(
                salle=selected_salle,
                medecin=current_medecin,
                date_used=timezone.now(),
                end_time=end_time
            )

    salles = Salle.objects.all()
    return render(request, 'demander_reservation.html', {'salles': salles})


@login_required
@user_passes_test(is_medecin)
def afficher_calendrier(request):
    current_medecin = Medecin.objects.get(user=request.user)
    current_date = datetime.now()
    rendezvous = RendezVous.objects.filter(medecin=current_medecin , date_heure__gte=current_date)
    return render(request, 'afficher_calendrier.html', {'rendezvous': rendezvous})

@login_required
@user_passes_test(is_medecin)
def modifier_informations(request):
    current_medecin = Medecin.objects.get(user=request.user)
    if request.method == 'POST':
        current_user = current_medecin.user
        current_user.nom = request.POST.get('nom')
        current_user.prenom = request.POST.get('prenom')
        current_user.email = request.POST.get('email')
        current_user.save()
        current_medecin.specialite = request.POST.get('specialite')
        current_medecin.save()
        return redirect('medecin')
    return render(request, 'modifier_informations.html', {'medecin': current_medecin})