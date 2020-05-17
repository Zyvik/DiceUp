from django import forms


class DiceUpForm(forms.Form):
    original_picture = forms.ImageField(label='Picture')
