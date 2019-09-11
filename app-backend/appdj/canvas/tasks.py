import logging

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from celery import shared_task

from appdj.servers.utils import email_to_username
from .models import CanvasInstance
from .lti import get_lti

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task()
def create_course_members(data):
    lti = get_lti(data)
    canvas_instance = CanvasInstance.objects.get(instance_guid=data['iss'])
    app = canvas_instance.applications.first()
    access_token = lti.get_access_token(
        canvas_instance.oidc_token_endpoint,
        settings.LTI_JWT_PRIVATE_KEY,
        app.client_id,
        'https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly'
    )
    headers = {
        'Accept': 'application/vnd.ims.lti-nrps.v2.membershipcontainer+json',
        'Authorization': '{token_type} {access_token}'.format(**access_token)
    }
    resp = requests.get(
        lti.context_memberships_url,
        headers=headers
    )
    resp.raise_for_status()
    out = resp.json()
    for member in out['members']:
        User.objects.get_or_create(
            email=member['email'],
            defaults=dict(
                username=email_to_username(member['email']),
                first_name=member.get('given_name', ''),
                last_name=member.get('family_name', ''),
            )
        )
