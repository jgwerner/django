import logging
from django.conf import settings as django_settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from users.models import Email
from .models import Notification, NotificationType, NotificationSettings
log = logging.getLogger('notifications')


def create_notification(user, actor, target, notif_type, signal=None):
    # TODO: Once we add more notification types, we will need to properly resolve
    # TODO: settings precedence
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

    notif_type, created = NotificationType.objects.get_or_create(name=notif_type)
    if created:
        log.info(f"Created new notification type: {notif_type}")

    notification = Notification(user=user,
                                actor=actor,
                                target=target,
                                type=notif_type,
                                is_active=settings.enabled)
    notification.save()
    log.info(f"Created notification {notification}")

    if settings.emails_enabled:
        log.info("Settings have enabled emails. Emailing notification.")
        template_name_str = f"notifications/{notif_type.template_name}."
        plaintext = get_template(template_name_str + "txt")
        html_text = get_template(template_name_str + "html")

        context = {'username': user.username}
        from_email = django_settings.DEFAULT_FROM_EMAIL
        to = [settings.email_address.address]

        text_content = plaintext.render(context)
        html_content = html_text.render(context)

        message = EmailMultiAlternatives(notif_type.subject, text_content, from_email, to)
        message.attach_alternative(html_content, "text/html")
        try:
            message.send(fail_silently=False)
            notification.emailed = True
            notification.save()
            log.info(f"Emailed notification.")
        except Exception as e:
            log.error(f"Unable to email notification: {notification}. Exception stacktrace:")
            log.exception(e)
