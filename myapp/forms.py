from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User,Patient,Medecin,Infirmiere,Rh

class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    is_admin = forms.BooleanField(label='Admin', required=False)

    class Meta:
        model = User
        fields = ('username','email','nom','prenom','password1','password2','is_rh','is_medecin','is_infermiere','is_visiteur','is_admin')

class AddPatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['medecin_traitant', 'raison_de_visite']

    nom = forms.CharField(max_length=100)
    prenom = forms.CharField(max_length=100)
    email = forms.EmailField()

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['medecin_traitant', 'raison_de_visite'] 

    nom = forms.CharField(max_length=100)
    prenom = forms.CharField(max_length=100)
    email = forms.EmailField()
    
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)

        # si patient existe
        if self.instance.user:
            self.fields['nom'].initial = self.instance.user.nom
            self.fields['prenom'].initial = self.instance.user.prenom
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        # Sauvegarder info -->  User instance associée
        if self.instance.user:
            self.instance.user.nom = self.cleaned_data['nom']
            self.instance.user.prenom = self.cleaned_data['prenom']
            self.instance.user.email = self.cleaned_data['email']
            self.instance.user.save()

        return super(PatientForm, self).save(commit)
    
class SelectDateForm(forms.Form):
       date_heure = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))