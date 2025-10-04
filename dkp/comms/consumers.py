import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from channels.layers import get_channel_layer
from .models import MessageLog


class AnesthetistConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Role name is hardcoded for AnesthetistConsumer since the URL pattern is specific
        self.role_name = 'Anesthetist'
        self.ward_id = self.scope['url_route']['kwargs']['ward_id']

        # Anesthetist monitors multiple channels in the ward
        self.group_names = [
            f"nurse_ward_{self.ward_id}",
            f"surgeon_ward_{self.ward_id}"
        ]

        # Join all relevant room groups
        for group_name in self.group_names:
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )

        # Join broadcast group for user count updates
        await self.channel_layer.group_add(
            'anesthetist_broadcast',
            self.channel_name
        )

        await self.accept()
        self.heartbeat_task = asyncio.create_task(self.send_heartbeat())

        # Don't track user count for anesthetist, they are only monitoring
        # await self.track_user_count(True)  # Removed - anesthetist should not be counted

    async def disconnect(self, close_code):
        if hasattr(self, 'heartbeat_task'):
            self.heartbeat_task.cancel()

        # Leave all room groups
        for group_name in self.group_names:
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )

        # Leave broadcast group
        await self.channel_layer.group_discard(
            'anesthetist_broadcast',
            self.channel_name
        )

        # Don't track user count for anesthetist
        # await self.track_user_count(False)  # Removed - anesthetist should not be counted

    async def send_heartbeat(self):
        while True:
            await asyncio.sleep(3)
            await self.send(text_data=json.dumps({
                'type': 'heartbeat',
                'timestamp': timezone.now().isoformat()
            }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'send_message':
            await self.handle_send_message(text_data_json)
        elif message_type == 'get_user_count':
            await self.send_user_count()

    async def handle_send_message(self, data):
        # Create message in database
        message = await database_sync_to_async(self._create_message_db)(data)

        # Get operating room name
        operating_room_name = await database_sync_to_async(self._get_operating_room_name)(data['operating_room_id'])

        # Determine target group based on recipient role
        recipient_role = data['recipient_role']
        ward_id = data['ward_id']

        if recipient_role.lower() == 'nurse':
            group_name = f"nurse_ward_{ward_id}"
        elif recipient_role.lower() == 'surgeon':
            group_name = f"surgeon_ward_{ward_id}"
        else:
            group_name = f"{recipient_role.lower()}_ward_{ward_id}"

        # Send to recipient's channel group
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'sender_role': data['sender_role'],
                'recipient_role': recipient_role,
                'message_type': data['message_type'],
                'content': data['message_type'],
                'location_type': 'ward',
                'location_id': int(ward_id),
                'operating_room_id': int(data['operating_room_id']),
                'operating_room_name': operating_room_name,
                'sent_at': message.sent_at.isoformat(),
            }
        )

        # Get user count for the target group
        count = await self.get_group_user_count(group_name)

        # Send status back to sender
        await self.send(text_data=json.dumps({
            'type': 'message_status',
            'message_id': message.id,
            'message_type': data['message_type'],
            'status': 'sent',
            'count': count,
            'timestamp': message.sent_at.isoformat()
        }))

    async def track_user_count(self, connecting):
        # Update user count for all groups
        for group_name in self.group_names:
            count = await self.update_user_count_in_redis(group_name, connecting)

            # Broadcast updated count to all Anesthetist consumers
            await self.channel_layer.group_send(
                'anesthetist_broadcast',
                {
                    'type': 'broadcast_user_count',
                    'group_name': group_name,
                    'count': count
                }
            )

    async def update_user_count_in_redis(self, group_name, connecting):
        from django.core.cache import cache

        # Get current count from cache
        current_count = cache.get(f"user_count:{group_name}")
        current_count = int(current_count) if current_count else 0

        # Update count
        if connecting:
            new_count = current_count + 1
        else:
            new_count = max(0, current_count - 1)

        # Store in cache with expiry
        cache.set(f"user_count:{group_name}", new_count, 3600)

        return new_count

    async def get_group_user_count(self, group_name):
        from django.core.cache import cache

        # Get count from cache
        count = cache.get(f"user_count:{group_name}")
        return int(count) if count else 0

    async def send_user_count(self):
        # Send current user counts for all monitored groups
        for group_name in self.group_names:
            count = await self.get_group_user_count(group_name)
            await self.send(text_data=json.dumps({
                'type': 'user_count',
                'group': group_name,
                'count': count
            }))

    def _create_message_db(self, data):
        from hospital.models import Role

        sender_role = Role.objects.get(name_en=data['sender_role'])
        recipient_role = Role.objects.get(name_en=data['recipient_role'])

        message = MessageLog.objects.create(
            sender_role=sender_role,
            recipient_role=recipient_role,
            message_type=data['message_type'],
            content=data['message_type'],
            location_type='operating_room',
            location_id=int(data['operating_room_id'])
        )
        return message

    def _get_message_details(self, message_id):
        try:
            message = MessageLog.objects.select_related('sender_role', 'recipient_role').get(id=message_id)
            return message
        except MessageLog.DoesNotExist:
            return None

    def _get_operating_room_name(self, operating_room_id):
        from hospital.models import OperatingRoom
        try:
            or_obj = OperatingRoom.objects.get(id=operating_room_id)
            return or_obj.name
        except OperatingRoom.DoesNotExist:
            return f"OR #{operating_room_id}"

    # Handle broadcast messages
    async def broadcast_user_count(self, event):
        # Only send if this is relevant to this anesthetist's ward
        if str(self.ward_id) in event['group_name']:
            await self.send(text_data=json.dumps({
                'type': 'user_count',
                'group': event['group_name'],
                'count': event['count']
            }))

    async def broadcast_acknowledgment(self, event):
        # Check if this acknowledgment is relevant to this anesthetist
        # For anesthetist messages sent from operating_room to ward, we need to check differently
        # The anesthetist is monitoring ward_id, but their messages have location_type='operating_room'
        # We need to check if this message was sent to the ward they're monitoring

        # Get the message details to determine if it's relevant
        message = await database_sync_to_async(self._get_message_details)(event['message_id'])

        if message:
            # Check if this message was sent from an anesthetist to the ward we're monitoring
            if (message.sender_role.name_en == 'Anesthetist' and
                message.location_type == 'operating_room'):
                # This is an anesthetist message - send the acknowledgment update
                await self.send(text_data=json.dumps({
                    'type': 'acknowledgment_update',
                    'message_id': event['message_id'],
                    'message_type': event['message_type'],
                    'acknowledged_at': event['acknowledged_at']
                }))

    async def broadcast_acknowledgment_from_or(self, event):
        # This method handles acknowledgments for messages sent from operating rooms
        # Send the acknowledgment update to the anesthetist who sent the message
        await self.send(text_data=json.dumps({
            'type': 'acknowledgment_update',
            'message_id': event['message_id'],
            'message_type': event['message_type'],
            'acknowledged_at': event['acknowledged_at']
        }))

    async def chat_message(self, event):
        # AnesthetistConsumer receives chat_message events because it monitors nurse/surgeon groups
        # But we don't need to display these messages to the Anesthetist since they sent them
        # Just silently ignore them to avoid the "No handler" error
        pass


class CommunicationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.role_name = self.scope['url_route']['kwargs']['role_name']
        self.location_type = self.scope['url_route']['kwargs']['location_type']
        self.location_id = self.scope['url_route']['kwargs']['location_id']

        self.room_group_name = f"{self.role_name.lower()}_{self.location_type}_{self.location_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send heartbeat message every 3 seconds
        self.heartbeat_task = asyncio.create_task(self.send_heartbeat())

        # Update user count in Redis
        await self.update_user_count(True)

        # Also initialize the count in cache if it doesn't exist
        from django.core.cache import cache
        cache_key = f"user_count:{self.room_group_name}"
        current_count = cache.get(cache_key)
        if current_count is None:
            cache.set(cache_key, 1, 3600)  # Initialize with 1 user (this one)

    async def disconnect(self, close_code):
        if hasattr(self, 'heartbeat_task'):
            self.heartbeat_task.cancel()

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Update user count in Redis
        await self.update_user_count(False)

    async def send_heartbeat(self):
        while True:
            await asyncio.sleep(3)
            await self.send(text_data=json.dumps({
                'type': 'heartbeat',
                'timestamp': timezone.now().isoformat()
            }))

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'acknowledge':
            message_id = text_data_json['message_id']
            role = text_data_json.get('role', self.role_name)  # Get role from client
            await self.acknowledge_message(message_id, role)
        elif message_type == 'send_message':
            await self.handle_send_message(text_data_json)

    async def acknowledge_message(self, message_id, acknowledging_role):
        # Update database
        message = await database_sync_to_async(self._acknowledge_message_db)(message_id)

        if message:
            # Get message details for broadcasting
            from hospital.models import Role

            # Check if this is a nurse or surgeon acknowledging a message sent to their role
            if acknowledging_role in ['Nurse', 'Surgeon'] and message.recipient_role.name_en == acknowledging_role:
                # Find all unacknowledged messages for this role in this location
                unacknowledged_messages = await database_sync_to_async(self._get_unacknowledged_messages_for_role)(
                    acknowledging_role, self.location_type, self.location_id
                )

                # Acknowledge all of them
                message_ids = []
                for msg in unacknowledged_messages:
                    await database_sync_to_async(self._acknowledge_message_db)(msg.id)
                    message_ids.append(msg.id)

                # Broadcast to all users of the same role in the same location
                await self.channel_layer.group_send(
                    self.room_group_name,  # This is the group for this role/location
                    {
                        'type': 'group_acknowledgment_broadcast',
                        'message_ids': message_ids,
                        'acknowledging_user': acknowledging_role,
                        'acknowledged_at': timezone.now().isoformat(),
                    }
                )

            # Also handle anesthetist notifications
            # Find which operating room this message came from
            # If it's from an operating room, we need to find anesthetists monitoring the relevant ward

            # Check if message was sent from an operating room to a ward
            if message.sender_role.name_en == 'Anesthetist' and message.location_type == 'operating_room':
                # Find all messages from this OR to get the target wards
                target_wards = await database_sync_to_async(
                    lambda: list(MessageLog.objects.filter(
                        sender_role_id=message.sender_role_id,
                        location_type='operating_room',
                        location_id=message.location_id
                    ).values_list('recipient_role', flat=True).distinct())
                )()

                # For simplicity, broadcast to all anesthetists monitoring any ward
                # They will filter based on which ward they're monitoring
                await self.channel_layer.group_send(
                    'anesthetist_broadcast',
                    {
                        'type': 'broadcast_acknowledgment_from_or',
                        'message_id': message.id,
                        'message_type': message.message_type,
                        'sender_role': message.sender_role.name,
                        'recipient_role': message.recipient_role.name,
                        'operating_room_id': message.location_id,
                        'acknowledged_at': message.acknowledged_at.isoformat(),
                    }
                )
            else:
                # Regular ward messages - broadcast to relevant anesthetists
                await self.channel_layer.group_send(
                    'anesthetist_broadcast',
                    {
                        'type': 'broadcast_acknowledgment',
                        'message_id': message.id,
                        'message_type': message.message_type,
                        'sender_role': message.sender_role.name,
                        'recipient_role': message.recipient_role.name,
                        'location_type': message.location_type,
                        'location_id': message.location_id,
                        'acknowledged_at': message.acknowledged_at.isoformat(),
                    }
                )

    def _acknowledge_message_db(self, message_id):
        try:
            message = MessageLog.objects.select_related('sender_role', 'recipient_role').get(id=message_id)
            if not message.acknowledged_at:  # Only acknowledge if not already acknowledged
                message.acknowledged_at = timezone.now()
                message.save()
            return message
        except MessageLog.DoesNotExist:
            return None

    def _get_unacknowledged_messages_for_role(self, role_name, location_type, location_id):
        from hospital.models import Role

        # Get the role object
        role = Role.objects.get(name_en=role_name)

        # Find all unacknowledged messages for this role in this location
        # Messages sent TO this role that haven't been acknowledged
        messages = MessageLog.objects.filter(
            recipient_role=role,
            acknowledged_at__isnull=True
        ).select_related('sender_role', 'recipient_role')

        # For nurses/surgeons, they receive messages in wards
        # So we need to filter by messages that were sent from anesthetists to their ward
        return messages

    async def update_user_count(self, connecting):
        from django.core.cache import cache
        from channels.layers import get_channel_layer

        # Get current count from cache
        current_count = cache.get(f"user_count:{self.room_group_name}")
        current_count = int(current_count) if current_count else 0

        # Update count
        if connecting:
            new_count = current_count + 1
        else:
            new_count = max(0, current_count - 1)

        # Store in cache with expiry
        cache.set(f"user_count:{self.room_group_name}", new_count, 3600)

        # Broadcast to anesthetists if this is a nurse or surgeon
        if self.role_name.lower() in ['nurse', 'surgeon']:
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                'anesthetist_broadcast',
                {
                    'type': 'broadcast_user_count',
                    'group_name': self.room_group_name,
                    'count': new_count
                }
            )

    async def handle_send_message(self, data):
        # Create message in database
        message = await database_sync_to_async(self._create_message_db)(data)

        # Send to recipient's channel group
        recipient_role = data['recipient_role']
        ward_id = data['ward_id']

        # For Anesthetist, messages go to ward locations
        location_type = 'ward'
        location_id = int(ward_id)

        group_name = f"{recipient_role.lower()}_ward_{ward_id}"

        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'sender_role': data['sender_role'],
                'recipient_role': recipient_role,
                'message_type': data['message_type'],
                'content': data['message_type'],
                'location_type': location_type,
                'location_id': location_id,
                'sent_at': message.sent_at.isoformat(),
            }
        )

    def _create_message_db(self, data):
        from hospital.models import Role

        sender_role = Role.objects.get(name_en=data['sender_role'])
        recipient_role = Role.objects.get(name_en=data['recipient_role'])

        # Handle both Anesthetist and regular user data formats
        if 'operating_room_id' in data:
            # Anesthetist sending from operating room
            location_type = 'operating_room'
            location_id = int(data['operating_room_id'])
        else:
            # Regular user
            location_type = data['location_type']
            location_id = int(data['location_id'])

        message = MessageLog.objects.create(
            sender_role=sender_role,
            recipient_role=recipient_role,
            message_type=data['message_type'],
            content=data['message_type'],
            location_type=location_type,
            location_id=location_id
        )
        return message

    # Receive message from room group
    async def chat_message(self, event):
        # Build message data
        message_data = {
            'type': 'message',
            'message_id': event['message_id'],
            'sender_role': event['sender_role'],
            'recipient_role': event['recipient_role'],
            'message_type': event['message_type'],
            'content': event['content'],
            'sent_at': event['sent_at'],
        }

        # Include operating room info if present (for messages from Anesthetist)
        if 'operating_room_id' in event:
            message_data['operating_room_id'] = event['operating_room_id']
            message_data['operating_room_name'] = event.get('operating_room_name', '')

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message_data))

    async def heartbeat(self, event):
        # Forward heartbeat to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'heartbeat',
            'timestamp': event['timestamp']
        }))

    async def group_acknowledgment_broadcast(self, event):
        # Forward broadcast acknowledgment to WebSocket
        # This is sent to all users of the same role in the same location
        await self.send(text_data=json.dumps({
            'type': 'broadcast_acknowledge',
            'message_ids': event['message_ids'],
            'acknowledging_user': event['acknowledging_user'],
            'acknowledged_at': event['acknowledged_at']
        }))