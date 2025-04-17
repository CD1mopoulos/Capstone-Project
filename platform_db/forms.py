from django import forms
from django.contrib.auth.forms import UserCreationForm
from platform_db.models import CustomUser, UserDetails

class CustomUserSignupForm(UserCreationForm):
    name = forms.CharField(max_length=150, required=True, label="Name")          # changed from full_name
    surename = forms.CharField(max_length=150, required=True, label="Surname")   # matches UserDetails
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['name', 'surename', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        """Override save method to update CustomUser and UserDetails"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['name']
        user.last_name = self.cleaned_data['surename']

        if commit:
            user.save()

            # ✅ Create related UserDetails entry
            UserDetails.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                surename=self.cleaned_data['surename']
            )

        return user