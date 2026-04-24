from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@shared_task
def send_invitation_email(email, name, token, base_url):
    invite_url = f"{base_url}auth/set-password/{token}/"
    subject = "Invitation to Join AloCentra"
    
    # Render HTML email template
    html_message = render_to_string('emails/invitation.html', {
        'name': name,
        'invitation_url': invite_url,
    })
    
    # Fallback plain text version
    message = f"Hello {name},\n\nYou have been invited to join AloCentra Exam Cell Platform.\n\nClick the link below to set your password and activate your account:\n{invite_url}\n\nThis link will expire in 48 hours.\n\nThank you,\nAloCentra Team"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
        html_message=html_message,
    )
    return f"Invitation sent to {email}"
