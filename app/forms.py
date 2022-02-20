from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from .models import Osde, Entidad, Software, Contrato, Servicio, Trabajo_Imp, Trabajo_Ofi
from django.contrib.auth.models import User
from django import forms

# OSDE ==========================================================================================================
class OsdeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['siglas_osde'].widget.attrs['autofocus'] = True

    class Meta():
        model = Osde
        fields = '__all__'
        widgets = {
            'siglas_osde': forms.TextInput(),
            'nombre_osde': forms.TextInput()
        }

# ENTIDAD =======================================================================================================
class EntidadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['nombre_entidad'].widget.attrs['autofocus'] = True

    class Meta():
        model = Entidad
        fields = '__all__'
        widgets = {
            'nombre_entidad': forms.TextInput()
        }

# SOFTWARE ======================================================================================================
class SoftwareForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['nombre_software'].widget.attrs['autofocus'] = True

    class Meta():
        model = Software
        fields = '__all__'
        widgets = {
            'nombre_software':forms.TextInput()
        }

# SERVICIO ======================================================================================================
class ServicioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['nombre_servicio'].widget.attrs['autofocus'] = True

    class Meta():
        model = Servicio
        fields = '__all__'
        widgets = {
            'nombre_servicio': forms.TextInput(),
            'costo':forms.NumberInput(),
        }

# CONTRATO ======================================================================================================
class ContratoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['osde'].widget.attrs['class'] = 'form-control select2'
        self.fields['entidad'].widget.attrs['class'] = 'form-control select2'
        self.fields['software'].widget.attrs['class'] = 'form-control select2'

    class Meta():
        model = Contrato
        fields = '__all__'
        widgets = {
            'osde': forms.Select(),
            'entidad':forms.Select(),
            'software': forms.Select(),
            'convenio':forms.TextInput(attrs={'placeholder': 'Convenio(Versat)'}),
            'concepto':forms.Select(),
            'tipo_base_datos':forms.Select(attrs={}),
            'cantidad_base_datos':forms.NumberInput(attrs={}),
            'vencimiento_licencia': forms.DateInput(attrs={'type': 'date'})
        }

#TRABAJO ========================================================================================================
class TrabImpForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['fecha'].widget.attrs['autofocus'] = True
        self.fields['entidad'].widget.attrs['class'] = 'form-control select2'
        self.fields['servicio'].widget.attrs['class'] = 'form-control select2'

    class Meta():
        model = Trabajo_Imp
        fields = '__all__'
        exclude = ['total']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'entidad':forms.Select(),
            'servicio': forms.Select(),
            'unidad_medida': forms.Select(),
            'cantidad': forms.NumberInput(),
            'implantador': forms.TextInput(attrs={'value':'', 'id':'implantador'}),
        }

class TrabajoOfiForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['fecha'].widget.attrs['autofocus'] = True
        self.fields['entidad'].widget.attrs['class'] = 'form-control select2'
        self.fields['servicio'].widget.attrs['class'] = 'form-control select2'
        self.fields['ofimatico'].widget.attrs['class'] = 'form-control select2'
        self.fields['ofimatico'].queryset = User.objects.filter(email__startswith='ofimatico')

    class Meta():
        model = Trabajo_Ofi
        fields = '__all__'
        exclude = ['total']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'entidad':forms.Select(),
            'servicio': forms.Select(),
            'unidad_medida': forms.Select(),
            'cantidad': forms.NumberInput(),
            'ofimatico': forms.Select(),
        }

# USUARIO =======================================================================================================
class UserCreateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['username'].widget.attrs['autofocus'] = True

    class Meta():
        model = User
        fields = 'username', 'first_name', 'last_name', 'email'
        widgets = {
            'username':forms.TextInput(),
            'first_name':forms.TextInput(),
            'last_name':forms.TextInput(),
            'email':forms.EmailInput(),
        }

class UserUpdateForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['username'].widget.attrs['autofocus'] = True
        self.fields['is_superuser'].widget.attrs['class'] = 'form-check'
        self.fields['is_active'].widget.attrs['class'] = 'form-check'
        self.fields['user_permissions'].widget.attrs['class'] = 'form-control select2'

    class Meta():
        model = User
        fields = 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_active', 'user_permissions'
        widgets = {
            'username':forms.TextInput(),
            'first_name':forms.TextInput(),
            'last_name':forms.TextInput(),
            'email':forms.EmailInput(),
            'user_permissions':forms.SelectMultiple(),
        }

class UserProfileForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['username'].widget.attrs['autofocus'] = True

    class Meta():
        model = User
        fields = 'username', 'first_name', 'last_name', 'email'
        widgets = {
            'username':forms.TextInput(),
            'first_name':forms.TextInput(),
            'last_name':forms.TextInput(),
            'email':forms.EmailInput(),
        }

class PasswordsChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['old_password'].widget.attrs['autofocus'] = True

    class Meta():
        model = User
        fields = '__all__'

class PasswordsResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['email'].widget.attrs['autofocus'] = True

    class Meta():
        model = User
        fields = '__all__'

class SetPasswordsForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['new_password1'].widget.attrs['autofocus'] = True

    class Meta():
        model = User
        fields = '__all__'