from django import forms 
from .models import User, CategoryArticle
from django.contrib.auth.forms import UserCreationForm

class CrearUsuario(UserCreationForm):
    class Meta:
        model = User

        fields = [
            'first_name',
            'last_name',
            'username',
            'password1',
            'email',
            'phone',
            'birth_date',
            'preferences',
        ]

        widgets = {
            'first_name' : forms.TextInput(attrs={'class':'ui fluid input', 'placeholder':'Ingresa el nombre de usuario aquí.'}),
            'last_name' : forms.TextInput(attrs={'class':'ui fluid input', 'placeholder':'Ingresa el nombre de usuario aquí.'}),
            'username' : forms.TextInput(attrs={'class':'ui fluid input', 'placeholder':'Ingresa el nombre de usuario aquí.'}),
            'password1' : forms.PasswordInput(),
            'password2' : forms.PasswordInput(),
            'email' : forms.TextInput(attrs={'class':'ui fluid input', 'placeholder':'Ingresa la  de correo aquí.'}),
            'preferences' : forms.SelectMultiple(),
            'birth_date' : forms.TextInput(attrs={'class':'ui fluid input', 'placeholder':'Ingresa la fecha de nacimiento de correo aquí.'}),
        }