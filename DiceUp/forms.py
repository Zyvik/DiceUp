from django import forms
from .models import validate_image


class DiceUpForm(forms.Form):
    original_picture = forms.ImageField(label='Picture',  validators=[validate_image])
