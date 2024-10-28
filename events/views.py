
from django.shortcuts import render, redirect,redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileForm, EventForm
from .models import UserProfile, Event, Booking
from django.core.exceptions import PermissionDenied




def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, "Account created successfully!")
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

@login_required
def profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'profile.html', {'profile_form': profile_form})

def event_list(request):
    events = Event.objects.all()
    booked_event_ids = []
    
    # Check booking status for logged-in users
    if request.user.is_authenticated:
        booked_events = Booking.objects.filter(user=request.user)
        booked_event_ids = [booking.event.id for booking in booked_events]
    
    return render(request, 'event_list.html', {'events': events, 'booked_event_ids': booked_event_ids})


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})


@login_required
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.created_by != request.user and not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'update_event.html', {'form': form})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.created_by != request.user and not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('event_list')
    return render(request, 'delete_event.html', {'event': event})


@login_required
def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.is_fully_booked():
        messages.error(request, "This event is fully booked.")
    elif Booking.objects.filter(user=request.user, event=event).exists():
        messages.info(request, "You have already booked this event.")
    else:
        Booking.objects.create(user=request.user, event=event)
        messages.success(request, "Event booked successfully!")
    return redirect('event_list')

@login_required
def booked_events(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booked_events.html', {'bookings': bookings})
