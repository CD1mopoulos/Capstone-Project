from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
import random, string

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to handle missing fields and prevent duplicate users."""

    def pre_social_login(self, request, sociallogin):
        """
        Before signing up a new user, check if the email already exists.
        If the user exists, log them in instead of creating a duplicate account.
        """
        email = sociallogin.account.extra_data.get("email")

        if not email:
            return  # If no email is provided, exit

        try:
            # Check if a user with this email already exists
            existing_user = User.objects.get(email=email)

            if sociallogin.is_existing:
                return  # If user is already linked, proceed normally

            # ✅ If user exists but is not linked to this social account, link it
            sociallogin.connect(request, existing_user)
            return

        except User.DoesNotExist:
            pass  # If no existing user, proceed with normal signup

    def save_user(self, request, sociallogin, form=None):
        """
        Ensure required fields (e.g., username, email, first_name) are populated.
        """
        user = sociallogin.user

        # ✅ Ensure the user has an email
        if not user.email:
            user.email = sociallogin.account.extra_data.get("email", "")

        # ✅ Ensure the user has a username (auto-generate if missing)
        if not user.username:
            user.username = self.generate_unique_username(user.email)

        # ✅ Ensure the user has a first name
        if not user.first_name:
            user.first_name = sociallogin.account.extra_data.get("first_name", "")

        # ✅ Ensure the user has a last name
        if not user.last_name:
            user.last_name = sociallogin.account.extra_data.get("last_name", "")

        user.save()
        return user

    def generate_unique_username(self, email):
        """
        Generate a unique username using the email or a random string if no email.
        """
        if email:
            base_username = email.split("@")[0]
        else:
            base_username = "user"

        # Append random characters to avoid duplicates
        return f"{base_username}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"