from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from authentication.models import UserFollows
from itertools import chain
from django.db.models import Q
from django.db import IntegrityError

from . import models
from . import forms


User = get_user_model()


# Create your views here.
@login_required
def home(request):
    # recupere tout les user qu'il suit
    follows = UserFollows.objects.filter(user=request.user)
    # fait un array des user suivis
    userfollows = []
    for userfollow in follows:
        userfollows.append(userfollow.followed_user)
    # recupere les tickets des user suivie et les siens
    tickets = models.Ticket.objects.filter(Q(user=request.user) | Q(user__in=userfollows))
    # recupere toute les reviews que le user a poster, ceux des user suivie et les reponses a ses tickets
    reviews = models.Review.objects.filter(Q(user=request.user) |
                                           Q(user__in=userfollows) |
                                           Q(ticket__user=request.user))
    # trie selon la date
    tickets_and_reviews = sorted(
        chain(tickets, reviews),
        key=lambda instance: instance.time_created,
        reverse=True
    )
    return render(request, 'blog/home.html', context={'tickets_and_reviews': tickets_and_reviews})


@login_required
def unfollow(request, id):
    try:
        follows = UserFollows.objects.get(pk=id, user=request.user)
    except User.DoesNotExist:
        return redirect("abonements")
    follows.delete()
    return redirect("abonements")


@login_required
def abonement(request):
    message = ""
    form = forms.SearchForm()
    # si post
    if request.method == 'POST':
        form = forms.SearchForm(request.POST)
        if form.is_valid():
            try:
                # recupere le user mais ne peut pas se suivre
                user = User.objects.exclude(pk=request.user.pk).get(username=form.cleaned_data["usernameFollows"])
            except User.DoesNotExist:
                message = "{} n'existe pas".format(form.cleaned_data["usernameFollows"])
            else:
                form.instance.user = request.user
                form.instance.followed_user = user
                try:
                    form.save()
                # erreur si suivie deja existant car ne peux exister qu'une seul fois
                except IntegrityError:
                    message = "vous suivez deja {}".format(form.cleaned_data["usernameFollows"])
                else:
                    message = "vous suivez l'utilisateur {}".format(user)
    # recupere ses follows
    try:
        follows = UserFollows.objects.filter(user=request.user)
    except UserFollows.DoesNotExist:
        follows = None
    # et les gens qu'il le suive
    try:
        followed_by = UserFollows.objects.filter(followed_user=request.user)
    except UserFollows.DoesNotExist:
        followed_by = None
    form = forms.SearchForm()
    return render(
        request,
        'blog/abonements.html',
        context={'form': form, "message": message, 'follows': follows, 'followed_by': followed_by}
        )


@login_required
def createTicket(request):
    form = forms.ticketForm()
    if request.method == 'POST':
        print(request.FILES)
        form = forms.ticketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            # ajoute le user
            ticket.user = request.user
            ticket.save()
            return redirect('home')
    return render(request, 'blog/createTicket.html', context={'form': form})


@login_required
def createNewReviews(request):
    formTicket = forms.ticketForm()
    formReview = forms.reviewForm()
    if request.method == 'POST':
        formTicket = forms.ticketForm(request.POST, request.FILES)
        formReview = forms.reviewForm(request.POST)
        if all([formTicket.is_valid() and formReview.is_valid()]):
            ticket = formTicket.save(commit=False)
            # ajout du user
            ticket.user = request.user
            print(formReview.cleaned_data["rating"])
            ticket.save()
            print(ticket)
            review = formReview.save(commit=False)
            # ajout du user
            review.user = request.user
            # ajout du ticket
            review.ticket = ticket
            review.save()
            return redirect('home')
    return render(request, 'blog/createReview.html', context={'formTicket': formTicket, 'formReview': formReview})


@login_required
def NewReviews(request, idticket):
    formReview = forms.reviewForm()
    ticketObj = models.Ticket.objects.get(pk=idticket)
    if request.method == 'POST':
        formReview = forms.reviewForm(request.POST)
        if formReview.is_valid():
            review = formReview.save(commit=False)
            # ajout du user
            review.user = request.user
            # ajout du ticket
            review.ticket = ticketObj
            review.save()
            return redirect('home')
    return render(request, 'blog/createReview.html', context={'ticket': ticketObj, 'formReview': formReview})


@login_required
def posts(request):
    # recupere les tickets du user
    tickets = models.Ticket.objects.filter(user=request.user)
    # recupere les reviews du user
    reviews = models.Review.objects.filter(user=request.user)
    # tri selon la date
    tickets_and_reviews = sorted(
        chain(tickets, reviews),
        key=lambda instance: instance.time_created,
        reverse=True
    )
    return render(request, 'blog/posts.html', context={'tickets_and_reviews': tickets_and_reviews})


@login_required
def changeTicket(request, idticket):
    ticket = models.Ticket.objects.get(pk=idticket)
    if request.method == 'POST':
        # si le ticket a une image il y a 2 forms
        if ticket.image:
            formTicket = forms.ticketForm(request.POST, instance=ticket)
            # form uniquement pour l'image
            formImg = forms.imgTicketForm(request.POST, request.FILES)
            if all([formTicket.is_valid(), formImg.is_valid()]):
                ticket = formTicket.save(commit=False)
                if formImg.cleaned_data["efface"]:
                    ticket.image = None
                elif formImg.cleaned_data["image"]:
                    ticket.image = formImg.cleaned_data["image"]
                ticket.save()
        else:
            formTicket = forms.ticketForm(request.POST, request.FILES, instance=ticket)
            formTicket.save()
        return redirect('posts')
    if ticket.image:
        # besoin de 2 forms pour simplifier la logique et le css
        formText = forms.textTicketForm(instance=ticket)
        formImg = forms.imgTicketForm()
        return render(request,
                      'blog/createTicket.html',
                      context={'formtext': formText, "ticket": ticket, "formimg": formImg}
                      )
    else:
        formTicket = forms.ticketForm(instance=ticket)
        return render(request, 'blog/createTicket.html', context={'form': formTicket})


@login_required
def changeReview(request, idreview):
    review = models.Review.objects.get(pk=idreview)
    formReview = forms.reviewForm(instance=review)
    if request.method == 'POST':
        formReview = forms.reviewForm(request.POST, instance=review)
        if formReview.is_valid():
            formReview.save()
            return redirect('posts')
    return render(request, 'blog/createReview.html', context={'ticket': review.ticket, 'formReview': formReview})


@login_required
def deleteTicket(request, idticket):
    ticket = models.Ticket.objects.get(pk=idticket)
    ticket.delete()
    return redirect('posts')


@login_required
def deleteReview(request, idreview):
    review = models.Review.objects.get(pk=idreview)
    review.delete()
    return redirect('posts')
