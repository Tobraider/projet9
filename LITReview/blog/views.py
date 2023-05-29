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
    follows = UserFollows.objects.filter(user=request.user)
    userfollows = []
    for userfollow in follows:
        userfollows.append(userfollow.followed_user)
    tickets = models.Ticket.objects.filter(Q(user=request.user) | Q(user__in=userfollows))
    reviews = models.Review.objects.filter(Q(user=request.user) |
                                           Q(user__in=userfollows) |
                                           Q(ticket__user=request.user))
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
    if request.method == 'POST':
        form = forms.SearchForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.exclude(pk=request.user.pk).get(username=form.cleaned_data["usernameFollows"])
            except User.DoesNotExist:
                message = "{} n'existe pas".format(form.cleaned_data["usernameFollows"])
            else:
                form.instance.user = request.user
                form.instance.followed_user = user
                try:
                    form.save()
                except IntegrityError:
                    message = "vous suivez deja {}".format(form.cleaned_data["usernameFollows"])
                else:
                    message = "vous suivez l'utilisateur {}".format(user)
    try:
        follows = UserFollows.objects.filter(user=request.user)
    except UserFollows.DoesNotExist:
        follows = None
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
            ticket.user = request.user
            print(formReview.cleaned_data["rating"])
            ticket.save()
            print(ticket)
            review = formReview.save(commit=False)
            review.user = request.user
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
            review.user = request.user
            review.ticket = ticketObj
            review.save()
            return redirect('home')
    return render(request, 'blog/createReview.html', context={'ticket': ticketObj, 'formReview': formReview})


@login_required
def posts(request):
    tickets = models.Ticket.objects.filter(user=request.user)
    reviews = models.Review.objects.filter(user=request.user)
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
        if ticket.image:
            formTicket = forms.ticketForm(request.POST, instance=ticket)
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
