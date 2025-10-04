from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # AnesthetistConsumer pattern MUST come first to match before the generic pattern
    # This pattern specifically handles Anesthetist connections to monitor wards
    re_path(r'ws/comms/Anesthetist/ward/(?P<ward_id>\d+)/$',
            consumers.AnesthetistConsumer.as_asgi()),
    # Generic pattern for all other roles (Nurse, Surgeon) connecting to their locations
    re_path(r'ws/comms/(?P<role_name>\w+)/(?P<location_type>\w+)/(?P<location_id>\d+)/$',
            consumers.CommunicationConsumer.as_asgi()),
]