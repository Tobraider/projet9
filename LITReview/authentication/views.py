from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from . import forms


def logout_user(request):
    logout(request)
    return redirect('login')


def login_page(request):
    # ne passe pas par cette page si deja connecté
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = forms.LoginForm()
        message = ''
        if request.method == 'POST':
            form = forms.LoginForm(request.POST)
            if form.is_valid():
                # fait l'authentification
                user = authenticate(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                )
                # si l'utilisateur est trouvé avec le jeu de données
                if user is not None:
                    login(request, user)
                    return redirect(settings.LOGIN_REDIRECT_URL)
                else:
                    message = 'Identifiants invalides.'
        return render(
            request, 'authentication/login.html', context={'form': form, 'message': message})


def signup_page(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        # bouton retour
        if 'return' in request.POST:
            return redirect("login")
        # bouton s'inscrire
        elif 'singup' in request.POST:
            form = forms.SignupForm(request.POST)
            if form.is_valid():
                print("ici")
                user = form.save()
                # connecte l'utilisateur directement
                login(request, user)
                return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'authentication/signup.html', context={'form': form})
