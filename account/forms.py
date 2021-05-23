from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from .models import *

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']



class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = []


class CreateBuyForm(forms.ModelForm):
    class Meta:
        model = Buy
        fields = []

class CreateSellForm(forms.ModelForm):
    class Meta:
        model = Sell
        fields = []