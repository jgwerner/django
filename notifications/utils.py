import logging
from django.conf import settings as django_settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from users.models import Email
from .models import Notification, NotificationType, NotificationSettings
log = logging.getLogger('notifications')


def create_notification(user, actor, target, notif_type, signal=None):
    settings, created = NotificationSettings.objects.get_or_create(user=user,
                                                                   entity="global",
                                                                   defaults={'enabled': True,
                                                                             'emails_enabled': True})
    if created:
        log.info(f"Global notification settings did not exist for user {user}, so they were created.")
        # This is the de facto default email address
        email = Email.objects.filter(user=user,
                                     address=user.email).first()
        settings.email_address = email
        settings.save()

    if settings.enabled:

        notif_type, created = NotificationType.objects.get_or_create(name=notif_type)
        if created:
            log.info(f"Created new notification type: {notif_type}")

        notification = Notification(user=user,
                                    actor=actor,
                                    target=target,
                                    type=notif_type)
        notification.save()
        log.info(f"Created notification {notification}")

        log.debug(("emails enabled?", settings.emails_enabled))
        if settings.emails_enabled:
            # send_mail(subject="3Blades notification",
            #           message=str(notification),
            #           from_email=django_settings.DEFAULT_FROM_EMAIL,
            #           recipient_list=[settings.email_address.address])
            plaintext = get_template(f"notifications/{notif_type.template_name}.txt")
            html_text = get_template(f"notifications/{notif_type.template_name}.html")

            context = {'username': user.username}
            subject = "Notification from 3Blades"
            from_email = django_settings.DEFAULT_FROM_EMAIL
            to = [settings.email_address.address]

            log.debug(("subject", subject, "from", from_email, "to", to))
            text_content = plaintext.render(context)
            html_content = html_text.render(context)

            message = EmailMultiAlternatives(notif_type.subject, text_content, from_email, to)
            message.attach_alternative(html_content, "text/html")
            message.send(fail_silently=False)
