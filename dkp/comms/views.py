from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.utils import translation
from django.contrib.sites.shortcuts import get_current_site
from datetime import timedelta
from hospital.models import Hospital, Role, OperatingRoom, Ward
from .models import MessageLog, MessageType


def role_selection(request):
    roles = Role.objects.all()

    # Get the hospital for the current site
    current_site = get_current_site(request)
    try:
        hospital = Hospital.objects.get(site=current_site)
    except Hospital.DoesNotExist:
        hospital = None

    # Get English role names for URLs
    # Temporarily disable translation to get English names
    from modeltranslation.utils import auto_populate
    roles_with_en = []

    # First, get the English names directly from the database
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM hospital_role")
        role_names = dict(cursor.fetchall())

    for role in roles:
        # Map role to its English name
        name_mapping = {
            1: 'Nurse',      # Pielęgniarka
            2: 'Anesthetist', # Anestezjolog
            3: 'Surgeon'      # Chirurg
        }
        roles_with_en.append({
            'role': role,
            'name_en': name_mapping.get(role.id, role.name)
        })

    return render(request, 'comms/role_selection.html', {
        'roles_with_en': roles_with_en,
        'hospital': hospital,
    })


def select_location(request, role_name):
    # Query using the untranslated field name_en
    role = Role.objects.get(name_en=role_name)

    if role.name_en == 'Anesthetist':
        locations = OperatingRoom.objects.all()
        location_type = 'operating_room'
        template = 'comms/select_location_anesthetist.html'
    else:  # Nurse or Surgeon
        locations = Ward.objects.all()
        location_type = 'ward'
        template = 'comms/select_location.html'

    # Get the untranslated role name for URLs
    role_name_en = role.name_en

    return render(request, template, {
        'role': role,
        'locations': locations,
        'location_type': location_type,
        'role_name_en': role_name_en,
    })


def select_ward_for_anesthetist(request, or_id):
    operating_room = OperatingRoom.objects.get(id=or_id)
    wards = Ward.objects.all()

    # Get the role from the session or query parameter
    # Since the URL doesn't include role, we need to determine it
    # Anesthetists are the only ones who go through this flow
    role = Role.objects.get(name_en='Anesthetist')

    role_name_en = role.name_en

    return render(request, 'comms/select_ward_for_anesthetist.html', {
        'operating_room': operating_room,
        'wards': wards,
        'role': role,
        'role_name_en': role_name_en,
    })


def communication_anesthetist(request, role_name, or_id, ward_id):
    role = Role.objects.get(name_en=role_name)
    operating_room = OperatingRoom.objects.get(id=or_id)
    ward = Ward.objects.get(id=ward_id)

    # Get recent messages sent from this OR to this ward
    messages = MessageLog.objects.filter(
        operating_room_id=or_id,
        ward_id=ward_id,
        recipient_role__name_en__in=['Nurse', 'Surgeon']
    ).select_related('sender_role', 'recipient_role', 'operating_room', 'ward').order_by('-sent_at')[:10]

    # Get message types available for anesthetist
    message_types = MessageType.objects.filter(
        source_role='Anesthetist',
        is_active=True
    ).order_by('display_order')

    # Get current language code
    current_language = translation.get_language()

    # Add localized descriptions to message types
    for msg_type in message_types:
        msg_type.short_description = msg_type.get_short_description(current_language)
        msg_type.full_description = msg_type.get_full_description(current_language)

    # Get the untranslated role name for WebSocket
    role_name_en = role.name_en

    return render(request, 'comms/communication_anesthetist.html', {
        'role': role,
        'operating_room': operating_room,
        'ward': ward,
        'messages': messages,
        'role_name_en': role_name_en,
        'message_types': message_types,
    })


def communication(request, role_name, location_type, location_id):
    role = Role.objects.get(name_en=role_name)

    if location_type == 'operating_room':
        location = OperatingRoom.objects.get(id=location_id)
    else:
        location = Ward.objects.get(id=location_id)

    # Get recent messages for this role and location
    # Filter messages from the last 2 hours only
    two_hours_ago = timezone.now() - timedelta(hours=2)

    if location_type == 'ward':
        # Nurses/Surgeons in wards receive messages sent to their ward
        messages = MessageLog.objects.filter(
            recipient_role=role,
            ward_id=location_id,
            sent_at__gte=two_hours_ago,
            acknowledged_at__isnull=True
        ).select_related('sender_role', 'recipient_role', 'operating_room', 'ward').order_by('-sent_at')
    else:
        # For operating rooms (if ever needed)
        messages = MessageLog.objects.filter(
            recipient_role=role,
            operating_room_id=location_id,
            sent_at__gte=two_hours_ago,
            acknowledged_at__isnull=True
        ).select_related('sender_role', 'recipient_role', 'operating_room', 'ward').order_by('-sent_at')

    # Get all roles for sending messages
    all_roles = Role.objects.all()

    # Get the untranslated role name for WebSocket
    role_name_en = role.name_en

    return render(request, 'comms/communication.html', {
        'role': role,
        'location': location,
        'location_type': location_type,
        'messages': messages,
        'all_roles': all_roles,
        'role_name_en': role_name_en,
    })


@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        sender_role_name = request.POST.get('sender_role')
        recipient_role_name = request.POST.get('recipient_role')
        message_type = request.POST.get('message_type')
        operating_room_id = request.POST.get('operating_room_id')
        ward_id = request.POST.get('ward_id')

        sender_role = Role.objects.get(name_en=sender_role_name)
        recipient_role = Role.objects.get(name_en=recipient_role_name)

        # Get hospital from operating room
        operating_room = OperatingRoom.objects.select_related('hospital').get(id=int(operating_room_id))
        hospital = operating_room.hospital

        # Create message log
        message = MessageLog.objects.create(
            hospital=hospital,
            sender_role=sender_role,
            recipient_role=recipient_role,
            message_type=message_type,
            content=message_type,
            operating_room_id=int(operating_room_id),
            ward_id=int(ward_id)
        )

        # Send via WebSocket
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()

        group_name = f"{recipient_role.name.lower()}_ward_{ward_id}"
        channel_layer.group_send(
            group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'sender_role': sender_role.name,
                'recipient_role': recipient_role.name,
                'message_type': message_type,
                'content': message.content,
                'operating_room_id': operating_room_id,
                'ward_id': ward_id,
                'sent_at': message.sent_at.isoformat(),
            }
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
def acknowledge_message(request):
    if request.method == 'POST':
        message_id = request.POST.get('message_id')

        try:
            message = MessageLog.objects.get(id=message_id)
            message.acknowledged_at = timezone.now()
            message.save()

            return JsonResponse({'status': 'success'})
        except MessageLog.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Message not found'}, status=404)

    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
def acknowledge_all_messages(request):
    if request.method == 'POST':
        role_name = request.POST.get('role_name')
        location_type = request.POST.get('location_type')
        location_id = request.POST.get('location_id')

        try:
            role = Role.objects.get(name_en=role_name)

            # Get all unacknowledged messages for this role and location from last 2 hours
            two_hours_ago = timezone.now() - timedelta(hours=2)

            if location_type == 'ward':
                messages = MessageLog.objects.filter(
                    recipient_role=role,
                    ward_id=location_id,
                    sent_at__gte=two_hours_ago,
                    acknowledged_at__isnull=True
                )
            else:
                messages = MessageLog.objects.filter(
                    recipient_role=role,
                    operating_room_id=location_id,
                    sent_at__gte=two_hours_ago,
                    acknowledged_at__isnull=True
                )

            # Acknowledge all messages
            count = messages.update(acknowledged_at=timezone.now())

            return JsonResponse({'status': 'success', 'count': count})
        except Role.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Role not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error'}, status=400)