from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from common.django_utils import AsyncFormMixin

class CustomPasswordChangeForm(PasswordChangeForm, AsyncFormMixin):
    """
    Custom password change form with better styling and translated labels
    """
    old_password = forms.CharField(
        label=_("Current Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label=_("New Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
    )
    
    async def asave(self, commit=True):
        """
        Async version of save method for password change form
        """
        user = self.user
        user.set_password(self.cleaned_data["new_password1"])
        if commit:
            await user.asave()
        return user 