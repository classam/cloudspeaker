from django import forms


class RegistrationForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
    password_again = forms.CharField(label="Password (Again)", widget=forms.PasswordInput())
