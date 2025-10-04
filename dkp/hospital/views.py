from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .models import Hospital, Ward, OperatingRoom
from .forms import HospitalForm, WardForm, OperatingRoomForm


@login_required
def dashboard(request):
    """Main dashboard for logged-in users"""
    current_site = get_current_site(request)
    try:
        hospital = Hospital.objects.get(site=current_site)
    except Hospital.DoesNotExist:
        hospital = None

    context = {
        'current_site': current_site,
        'hospital': hospital,
    }
    return render(request, 'hospital/dashboard.html', context)


# Hospital Views
@login_required
def hospital_edit(request):
    """Edit the current site's hospital information"""
    current_site = get_current_site(request)
    try:
        hospital = Hospital.objects.get(site=current_site)
    except Hospital.DoesNotExist:
        messages.error(request, 'No hospital configured for this site.')
        return redirect('hospital:dashboard')

    if request.method == 'POST':
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            hospital = form.save()
            messages.success(request, f'Hospital "{hospital.name}" updated successfully.')
            return redirect('hospital:dashboard')
    else:
        form = HospitalForm(instance=hospital)
    return render(request, 'hospital/hospital_form.html', {'form': form, 'action': 'Edit', 'hospital': hospital})


# Ward Views
@login_required
def ward_list(request):
    wards = Ward.objects.all().select_related('hospital')
    return render(request, 'hospital/ward_list.html', {'wards': wards})


@login_required
def ward_create(request):
    # Get the hospital for the current site
    current_site = get_current_site(request)
    try:
        site_hospital = Hospital.objects.get(site=current_site)
    except Hospital.DoesNotExist:
        site_hospital = None

    if request.method == 'POST':
        form = WardForm(request.POST, user=request.user, site_hospital=site_hospital)
        if form.is_valid():
            ward = form.save(commit=False)
            # For non-superusers, ensure the hospital is set from the site
            if not request.user.is_superuser and site_hospital:
                ward.hospital = site_hospital
            ward.save()
            messages.success(request, f'Ward "{ward.name}" created successfully.')
            return redirect('hospital:ward_list')
    else:
        form = WardForm(user=request.user, site_hospital=site_hospital)
    return render(request, 'hospital/ward_form.html', {'form': form, 'action': 'Create'})


@login_required
def ward_edit(request, pk):
    ward = get_object_or_404(Ward, pk=pk)
    # Get the hospital for the current site
    current_site = get_current_site(request)
    try:
        site_hospital = Hospital.objects.get(site=current_site)
    except Hospital.DoesNotExist:
        site_hospital = None

    if request.method == 'POST':
        form = WardForm(request.POST, instance=ward, user=request.user, site_hospital=site_hospital)
        if form.is_valid():
            ward = form.save(commit=False)
            # For non-superusers, ensure the hospital remains unchanged
            if not request.user.is_superuser:
                ward.hospital = get_object_or_404(Ward, pk=pk).hospital
            ward.save()
            messages.success(request, f'Ward "{ward.name}" updated successfully.')
            return redirect('hospital:ward_list')
    else:
        form = WardForm(instance=ward, user=request.user, site_hospital=site_hospital)
    return render(request, 'hospital/ward_form.html', {'form': form, 'action': 'Edit', 'ward': ward})


@login_required
def ward_delete(request, pk):
    ward = get_object_or_404(Ward, pk=pk)
    if request.method == 'POST':
        name = ward.name
        ward.delete()
        messages.success(request, f'Ward "{name}" deleted successfully.')
        return redirect('hospital:ward_list')
    return render(request, 'hospital/ward_confirm_delete.html', {'ward': ward})


# Operating Room Views
@login_required
def operating_room_list(request):
    operating_rooms = OperatingRoom.objects.all().select_related('hospital')
    return render(request, 'hospital/operating_room_list.html', {'operating_rooms': operating_rooms})


@login_required
def operating_room_create(request):
    # Get the hospital for the current site
    current_site = get_current_site(request)
    try:
        site_hospital = Hospital.objects.get(site=current_site)
    except Hospital.DoesNotExist:
        site_hospital = None

    if request.method == 'POST':
        form = OperatingRoomForm(request.POST, user=request.user, site_hospital=site_hospital)
        if form.is_valid():
            operating_room = form.save(commit=False)
            # For non-superusers, ensure the hospital is set from the site
            if not request.user.is_superuser and site_hospital:
                operating_room.hospital = site_hospital
            operating_room.save()
            messages.success(request, f'Operating Room "{operating_room.name}" created successfully.')
            return redirect('hospital:operating_room_list')
    else:
        form = OperatingRoomForm(user=request.user, site_hospital=site_hospital)
    return render(request, 'hospital/operating_room_form.html', {'form': form, 'action': 'Create'})


@login_required
def operating_room_edit(request, pk):
    operating_room = get_object_or_404(OperatingRoom, pk=pk)
    # Get the hospital for the current site
    current_site = get_current_site(request)
    try:
        site_hospital = Hospital.objects.get(site=current_site)
    except Hospital.DoesNotExist:
        site_hospital = None

    if request.method == 'POST':
        form = OperatingRoomForm(request.POST, instance=operating_room, user=request.user, site_hospital=site_hospital)
        if form.is_valid():
            operating_room = form.save(commit=False)
            # For non-superusers, ensure the hospital remains unchanged
            if not request.user.is_superuser:
                operating_room.hospital = get_object_or_404(OperatingRoom, pk=pk).hospital
            operating_room.save()
            messages.success(request, f'Operating Room "{operating_room.name}" updated successfully.')
            return redirect('hospital:operating_room_list')
    else:
        form = OperatingRoomForm(instance=operating_room, user=request.user, site_hospital=site_hospital)
    return render(request, 'hospital/operating_room_form.html', {'form': form, 'action': 'Edit', 'operating_room': operating_room})


@login_required
def operating_room_delete(request, pk):
    operating_room = get_object_or_404(OperatingRoom, pk=pk)
    if request.method == 'POST':
        name = operating_room.name
        operating_room.delete()
        messages.success(request, f'Operating Room "{name}" deleted successfully.')
        return redirect('hospital:operating_room_list')
    return render(request, 'hospital/operating_room_confirm_delete.html', {'operating_room': operating_room})