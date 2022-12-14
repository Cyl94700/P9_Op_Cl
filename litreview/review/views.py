from itertools import chain
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review, Ticket
from .forms import TicketForm, TicketFormDelete, ReviewForm, ReviewFormDelete
from . import forms, models
from django.db.models import Q


@login_required
def feed(request):
    tickets = models.Ticket.objects.filter(
       Q(user__in=request.user.follows.all()) |
       Q(user__exact=request.user.id))

    reviews = models.Review.objects.filter(
       Q(user__in=request.user.follows.all()) |
       Q(user__exact=request.user.id))

    tickets_and_reviews = sorted(
        chain(tickets, reviews),
        key=lambda instance: instance.time_created,
        reverse=True
    )

    paginator = Paginator(tickets_and_reviews, 6)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    context = {
        'page_obj': page_obj,
        'tickets': tickets,
        'reviews': reviews
    }

    return render(
        request,
        'review/feed.html',
        context
     )


@login_required
def create_ticket(request):
    form = forms.TicketForm()
    if request.method == 'POST':
        form = forms.TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, f'Votre ticket a bien été créée!')
            return redirect('feed')
    context = {
        'form': form
    }
    return render(
        request,
        'review/create_ticket.html',
        context
    )


@login_required
def create_review(request, ticket_id):
    form = forms.ReviewForm()
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = get_object_or_404(models.Ticket, id=ticket_id)
            review.ticket.has_review = True
            review.ticket.save()
            review.save()
            messages.success(request, f'Votre critique a bien été créée!')
            return redirect('feed')
    context = {
        'both': False,
        'form': form
    }
    return render(
        request,
        'review/create_review.html',
        context
    )


@login_required
def create_ticket_and_review(request):
    ticket_form = forms.TicketForm()
    review_form = forms.ReviewForm()
    if request.method == 'POST':
        ticket_form = forms.TicketForm(request.POST, request.FILES)
        review_form = forms.ReviewForm(request.POST)
        if all([ticket_form.is_valid(), review_form.is_valid()]):
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            # if ticket_form.cleaned_data['image']:
            # ticket.image = ticket_form.cleaned_data['image']
            ticket.has_review = True
            ticket.save()
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = get_object_or_404(models.Ticket, id=ticket.id)
            review.save()
            messages.success(request, f'Votre publication a bien été créée!')
            return redirect('feed')
    context = {
        'both': True,
        'ticket_form': ticket_form,
        'review_form': review_form
    }
    return render(
        request,
        'review/create_review.html',
        context
    )


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(models.Ticket, id=ticket_id)
    edit_form = forms.TicketForm(instance=ticket)
    delete_form = forms.TicketFormDelete()
    if ticket.user != request.user:
        raise PermissionDenied()
    if request.method == 'POST':
        if 'edit_ticket' in request.POST:
            edit_form = forms.TicketForm(request.POST, request.FILES, instance=ticket)
            if edit_form.is_valid():
                print(edit_form.fields['image'])
                edit_form.save()
                messages.success(request, f'Votre ticket a bien été modifié!')
                return redirect('feed')
        if 'delete_ticket' in request.POST:
            delete_form = forms.TicketFormDelete(request.POST)
            if delete_form.is_valid():
                ticket.delete()
                messages.success(request, f'Votre ticket a bien été supprimé!')
                return redirect('feed')
    context = {
        'edit_form': edit_form,
        'ticket': ticket,
        'delete_form': delete_form
    }
    return render(
        request,
        'review/edit_ticket.html',
        context
    )


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(models.Review, id=review_id)
    edit_form = forms.ReviewForm(instance=review)
    delete_form = forms.ReviewFormDelete()
    if review.user != request.user:
        raise PermissionDenied()
    if request.method == 'POST':
        if 'edit_review' in request.POST:
            edit_form = forms.ReviewForm(request.POST, instance=review)
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, f'Votre critique a bien été modifié!')
                return redirect('feed')
        if 'delete_review' in request.POST:
            delete_form = forms.ReviewFormDelete(request.POST)
            if delete_form.is_valid():
                review.delete()
                messages.success(request, f'Votre critique a bien été supprimée!')
                return redirect('feed')
    context = {
        'edit_form': edit_form,
        'delete_form': delete_form
    }
    return render(
        request,
        'review/edit_review.html',
        context
    )


@login_required
def ticket_view(request):
    tickets = models.Ticket.objects.filter(
        Q(user__in=request.user.follows.all()) |
        Q(user__exact=request.user.id))
    tickets = sorted(
        chain(tickets),
        key=lambda instance: instance.time_created,
        reverse=True)

    paginator = Paginator(tickets, 6)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    context = {
        'page_obj': page_obj,
        'tickets': tickets
    }

    return render(
        request,
        'review/ticket_view.html',
        context
     )


@login_required
def review_view(request):
    reviews = models.Review.objects.filter(
        Q(user__in=request.user.follows.all()) |
        Q(user__exact=request.user.id))
    reviews = sorted(
        chain(reviews),
        key=lambda instance: instance.time_created,
        reverse=True)

    paginator = Paginator(reviews, 6)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    context = {
        'page_obj': page_obj,
        'reviews': reviews
    }

    return render(
        request,
        'review/review_view.html',
        context
     )
