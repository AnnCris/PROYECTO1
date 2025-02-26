from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm,  UserChangeForm
from django.core.validators import RegexValidator
from .models import UsuarioPersonalizado, Rol

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario o Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario o email'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    
class RegistroForm(UserCreationForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[
            RegexValidator(
                regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                message='La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas, números y caracteres especiales'
            )
        ]
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = UsuarioPersonalizado
        fields = ('username', 'email', 'password1', 'password2', 'rol')
        
class UsuarioPersonalizadoChangeForm(UserChangeForm):
    class Meta:
        model = UsuarioPersonalizado
        fields = ('username', 'email', 'first_name', 'last_name', 'rol')       