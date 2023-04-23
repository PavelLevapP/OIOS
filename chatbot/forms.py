from django import forms
from .models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User

        fields = ('telegram_id', 'user_name', 'first_name', 'last_name', 'password')

