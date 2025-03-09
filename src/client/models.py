from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _t
from django.utils.translation import gettext as _t2
from django.core.exceptions import ObjectDoesNotExist

from asgiref.sync import sync_to_async

from account.models import CustomUser

PLAN_CHOICE_NAME_MAX_LEN = 30
SUBSCRIPTION_COST_MAX_DIGITS = 4
PLAN_CHOICE_DESC_MAX_LEN = 300
EXTERNAL_ID_MAX_LEN = 255
EXTERNAL_API_URL_MAX_LEN = 2000
EXTERNAL_STYLE_MAX_LEN = 2000


class PlanChoice(models.Model):
    plan_code = models.CharField(
        max_length = 2, unique = True, blank = False,
        verbose_name=_t('Plan code')
    )
    name = models.CharField(
        max_length = PLAN_CHOICE_NAME_MAX_LEN, unique = True, blank = False,
        verbose_name = _t('Plan name')
    )
    cost = models.DecimalField(
        max_digits = SUBSCRIPTION_COST_MAX_DIGITS, decimal_places = 2,
        verbose_name = _t('Plan cost')
    )
    is_active = models.BooleanField(default = False)
    date_added = models.DateTimeField(default = timezone.now)
    date_changed = models.DateTimeField(default = timezone.now)

    description1 = models.CharField(
        max_length = PLAN_CHOICE_DESC_MAX_LEN, verbose_name = _t('Plan description 1')
    )
    description2 = models.CharField(
        max_length = PLAN_CHOICE_DESC_MAX_LEN, verbose_name = _t('Plan description 2')
    )
    external_plan_id = models.CharField(
        max_length = EXTERNAL_ID_MAX_LEN, unique = True, verbose_name = _t('External plan ID')
    )
    external_api_url = models.CharField(
        max_length = EXTERNAL_API_URL_MAX_LEN, verbose_name = _t('External API URL')
    )
    external_style_json = models.CharField(
        max_length = EXTERNAL_STYLE_MAX_LEN, verbose_name = _t('External style JSON')
    )

    def __str__(self) -> str:
        return f"{str(self.name)} subscription"
    
    @classmethod
    def from_plan_code(cls, plan_code: str) -> 'PlanChoice':
        return PlanChoice.objects.get(plan_code = plan_code)
    
    @classmethod
    async def afrom_plan_code(cls, plan_code: str) -> 'PlanChoice':
        return await PlanChoice.objects.aget(plan_code = plan_code)


class Subscription(models.Model):
    cost = models.DecimalField(
        max_digits = SUBSCRIPTION_COST_MAX_DIGITS, decimal_places = 2, verbose_name = _t('Cost')
    )

    external_subscription_id = models.CharField(
        max_length = EXTERNAL_ID_MAX_LEN, verbose_name = _t('External subscription ID')
    )

    is_active = models.BooleanField(default = False)
    date_added = models.DateTimeField(default = timezone.now)
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE)
    plan_choice = models.ForeignKey(PlanChoice, on_delete = models.CASCADE)

    def __str__(self) -> str:
        plan_choice = self.plan_choice
        return f'{self.user.first_name} {self.user.last_name}: {plan_choice.name} {_t2("subscription")}'

    async def aplan_choice(self) -> PlanChoice:
        @sync_to_async
        def call_sync_fk() -> PlanChoice:
            return self.plan_choice
        return await call_sync_fk()


    async def ais_premium(self) -> bool:
        return (await self.aplan_choice()).plan_code == 'PR'

    async def ais_standard(self) -> bool:
        return (await self.aplan_choice()).plan_code == 'ST'
    
    @staticmethod
    async def afor_user(user: CustomUser, status = '') -> 'Subscription | None':
        kargs: dict = {'user': user}
        if status in ('A', 'I'):
            kargs.update(is_active = (status == 'A'))
        try:
            return await Subscription.objects.aget(**kargs)
        except ObjectDoesNotExist:
            return None