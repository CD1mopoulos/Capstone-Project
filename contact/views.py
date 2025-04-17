from django.shortcuts import render, redirect
from platform_db.models import GeneralComment, UserDetails
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings


def contact(request):
    user_details = None

    if request.user.is_authenticated:
        try:
            user_details = request.user.userdetails
        except UserDetails.DoesNotExist:
            # Auto-create blank UserDetails if it doesn't exist
            user_details = UserDetails.objects.create(user=request.user)

    return render(request, "contact/contact.html", {"user_details": user_details})


@login_required
def submit_comment(request):
    if request.method == 'POST':
        comment_text = request.POST.get('review', '').strip()
        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()

        if comment_text:
            GeneralComment.objects.create(
                user=request.user,
                name=name,
                surname=surname,
                comment=comment_text
            )
            messages.success(request, "Your comment has been submitted successfully!")
        else:
            messages.error(request, "Comment text cannot be empty.")

    return redirect('contact:contact')


def send_contact_email(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"""
        Hello {name},

        We have received your message regarding: "{subject}"

        Here is what you submitted:
        - Full Name: {name}
        - Email: {email}
        - Phone Number: {phone or 'N/A'}
        - Subject: {subject}
        - Message: {message}

        We appreciate your feedback or concerns. Our team will get back to you shortly!

        Kind regards,  
        NomNomNow Team
        """

        send_mail(
            subject='Your message has been received - NomNomNow',
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect('contact:contact')  # or show a success page

    return redirect('contact:contact')