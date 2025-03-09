from django.forms import ModelForm

from account.models import CustomUser
from common.django_utils import AsyncModelFormMixin

class UpdateUserForm(AsyncModelFormMixin, ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
        )
