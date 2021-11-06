from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.utils.safestring import mark_safe

from .models import *
from django.core.mail import send_mail


class LoginForm(forms.Form):
    username = forms.CharField(label='Login', max_length=120)
    password = forms.CharField(label='Hasło', max_length=120, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'input'

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class EditProfileForm(forms.Form):
    username = forms.CharField(label='login')
    # profile_picture = forms.ImageField(label='Zdjęcie profilowe', required=False)
    first_name = forms.CharField(label='Imię', required=False)
    last_name = forms.CharField(label='Nazwisko', required=False)
    email = forms.EmailField(label='e-mail')


class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    repeat_password = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'input'

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        username = cleaned_data.get("username")
        repeat_password = cleaned_data.get("repeat_password")

        if password is not None and password != repeat_password:
            self.add_error("repeat_password", "Hasła muszą być takie same.")

        if User.objects.filter(username=username):
            self.add_error('username', 'Login zajęty. Wybierz inny.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
