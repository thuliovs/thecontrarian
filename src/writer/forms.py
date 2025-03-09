from django.forms import ModelForm

from account.models import CustomUser
from common.django_utils import AsyncModelFormMixin
from writer.models import Article


class ArticleForm(AsyncModelFormMixin, ModelForm):
    class Meta:
        model = Article
        fields = (
            'title',
            'content',
            'is_premium',
        )

class UpdateUserForm(AsyncModelFormMixin, ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
        )
