import logging
from django.conf import settings as django_settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from users.models import Email, User
from .models import Notification, NotificationType, NotificationSettings
log = logging.getLogger('notifications')


def create_notification(user: User, actor, target, entity: str, notif_type: str) -> None:
    # TODO: Once we add more notification types, we will need to properly resolve
    # TODO: settings precedence
    settings, created = NotificationSettings.objects.get_or_create(user=user,
                                                                   entity=entity,
                                                                   defaults={'enabled': True,
                                                                             'emails_enabled': True})
    if created:
        log.info(f"{entity} notification settings did not exist for user {user}, so they were created.")
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

    if notif_type.entity == "billing" or settings.emails_enabled:
        log.info("Settings have enabled emails. Emailing notification.")
        template_name_str = f"notifications/{notif_type.template_name}."

        try:
            plaintext = get_template(template_name_str + "txt")
            html_text = get_template(template_name_str + "html")
        except Exception as e:
            log.error(f"Unable to find template {template_name_str} for notification type {notif_type.name}."
                      f"Will not be able to email notification. This is a problem!!")
            log.exception(e)
            return

        user_name_to_use = user.first_name or user.username

        context = {'username': user_name_to_use,
                   'actor': actor,
                   'target': target}
        from_email = django_settings.DEFAULT_FROM_EMAIL
        to = [user.email]

        text_content = plaintext.render(context)
        html_content = html_text.render(context)

        message = EmailMultiAlternatives(notif_type.subject, text_content, from_email, to)
        message.attach_alternative(html_content, "text/html")
        try:
            message.send(fail_silently=False)
        except Exception as e:
            log.error(f"Unable to email notification: {notification}. Exception stacktrace:")
            log.exception(e)

        notification.emailed = True
        notification.save()
        log.info(f"Emailed notification.")
