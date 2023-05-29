from django import forms
from authentication.models import UserFollows
from . import models


class SearchForm(forms.ModelForm):
    usernameFollows = forms.CharField(max_length=63,
                                      label="",
                                      widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"})
                                      )

    class Meta:
        model = UserFollows
        fields = ['usernameFollows']


class ticketForm(forms.ModelForm):
    title = forms.CharField(max_length=128, label="Titre", widget=forms.TextInput())
    description = forms.CharField(required=False, widget=forms.Textarea(), label="Description", max_length=2048)
    image = forms.ImageField(label="Image", required=False, widget=forms.ClearableFileInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = models.Ticket
        fields = ['title', "description", "image"]


class textTicketForm(forms.ModelForm):
    title = forms.CharField(max_length=128, label="Titre", widget=forms.TextInput())
    description = forms.CharField(required=False, widget=forms.Textarea(), label="Description", max_length=2048)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = models.Ticket
        fields = ['title', "description"]


class imgTicketForm(forms.Form):
    image = forms.ImageField(label="Choisir une autre image", required=False, widget=forms.ClearableFileInput())
    efface = forms.BooleanField(label="Supprimer l'image", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''


class reviewForm(forms.ModelForm):
    CHOICES = [
        (0, ' - 0'),
        (1, ' - 1'),
        (2, ' - 2'),
        (3, ' - 3'),
        (4, ' - 4'),
        (5, ' - 5'),
    ]
    rating = forms.ChoiceField(
        label="Note",
        widget=forms.RadioSelect,
        choices=CHOICES,
    )
    body = forms.CharField(required=False, widget=forms.Textarea(), label="Description", max_length=2048)
    headline = forms.CharField(max_length=128, label="Titre", widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = models.Review
        fields = ['headline', "rating", "body"]
