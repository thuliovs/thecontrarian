from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth import update_session_auth_hash
from asgiref.sync import sync_to_async

from .models import Subscription, PlanChoice
from writer.models import Article
from common.django_utils import arender, add_message, alogout
from common.auth import aclient_required, ensure_for_current_user # type: ignore
from common.auth import aget_user
from . import paypal as sub_manager
from .forms import UpdateUserForm
from common.forms import CustomPasswordChangeForm

# Criar uma versão assíncrona da função update_session_auth_hash
async_update_session_auth_hash = sync_to_async(update_session_auth_hash)

@aclient_required
async def dashboard(request: HttpRequest) -> HttpResponse:
    user = await aget_user(request)
    subscription_plan = 'No subscription yet'
    if subscription := await Subscription.afor_user(user):
        subscription_plan = 'premium' if await subscription.ais_premium() else 'standard'
        if not subscription.is_active:
            subscription_plan += ' (inactive)'
    try:
        subscription = await Subscription.objects.aget(user = user, is_active = True)
        has_subscription = True
        subscription_name = (await subscription.aplan_choice()).name
    except ObjectDoesNotExist:
        has_subscription = False
        subscription_name = 'No subscription yet'

    context = {
        'has_subscription': has_subscription,
        'subscription_plan': subscription_plan,
        'subscription_name': subscription_name
    }
    return await arender(request, 'client/dashboard.html', context)

@aclient_required
async def browse_articles(request: HttpRequest) -> HttpResponse:
    user = await aget_user(request)
    try:
        subscription = await Subscription.objects.aget(user = user, is_active = True)
        has_subscription = True
        subscription_plan = 'premium' if await subscription.ais_premium() else 'standard'
        if not await subscription.ais_premium():
            articles = Article.objects.filter(is_premium = False).select_related('user')
        else:
            articles = Article.objects.all().select_related('user')
    except ObjectDoesNotExist:
        has_subscription = False
        subscription_plan = 'none'
        articles = []

    context = {
        'has_subscription': has_subscription, 
        'articles': articles,
        'subscription_plan': subscription_plan,
    }
    return await arender(request, 'client/browse-articles.html', context)

@aclient_required
async def subscribe_plan(request: HttpRequest) -> HttpResponse:
    user = await aget_user(request)
    if await Subscription.afor_user(user):
        return redirect('client-dashboard')
    context = {'plan_choices': PlanChoice.objects.filter(is_active = True)}
    return await arender(request, 'client/subscribe-plan.html', context)

@aclient_required
async def update_user(request: HttpRequest) -> HttpResponse:
    user = await aget_user(request)
    
    # Inicializa o formulário para GET e só substitui para POST se necessário
    form = UpdateUserForm(instance=user)
    
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance = user)
        if await form.ais_valid():
            await form.asave()
            # Adiciona mensagem de sucesso usando a função auxiliar
            await add_message(request, messages.INFO, _('User updated successfully'))
            return redirect('update-client')
        else:
            # Adiciona mensagem de erro usando a função auxiliar
            await add_message(request, messages.ERROR, _('Error updating user information'))
            form = UpdateUserForm(instance = user)
    try:
        subscription = await Subscription.objects.aget(user = user, is_active = True)
        has_subscription = True
        subscription_plan = 'premium' if await subscription.ais_premium() else 'standard'
        subscription_name = (await subscription.aplan_choice()).name
    except ObjectDoesNotExist:
        subscription = None
        has_subscription = False
        subscription_plan = 'none'
        subscription_name = 'No subscription yet'

    context = {
        'has_subscription': has_subscription,
        'subscription_plan': subscription_plan,
        'subscription_name': subscription_name,
        'subscription': subscription,
        'update_user_form': form,
    }
    return await arender(request, 'client/update-user.html', context)

@aclient_required
async def create_subscription(
    request: HttpRequest,
    sub_id: str,
    plan_code: str,
) -> HttpResponse:
    user = await aget_user(request)

    if await Subscription.afor_user(user):
        return redirect('client-dashboard')

    plan_choice = await PlanChoice.afrom_plan_code(plan_code)
    await Subscription.objects.acreate(
        plan_choice = plan_choice,
        cost = plan_choice.cost,
        external_subscription_id = sub_id,
        is_active = True,
        user = user,
    )

    # Adicionar mensagem de sucesso
    await add_message(request, messages.SUCCESS, _('Your subscription has been successfully activated'))
    
    # Redirecionar para a página de atualização do usuário em vez da página de confirmação
    return redirect('update-client')


@aclient_required
@ensure_for_current_user(Subscription, redirect_if_missing = 'client-dashboard')
async def cancel_subscription(request: HttpRequest, id: int) -> HttpResponse:
    subscription = id

    if request.method == 'POST':
        # Cancel the subscription in PayPal
        access_token = await sub_manager.get_access_token()
        sub_id = subscription.external_subscription_id
        await sub_manager.cancel_subscription(access_token, sub_id)

        # Update the subscription in the database
        await subscription.adelete()
        
        # Adicionar mensagem de informação
        await add_message(request, messages.INFO, _('Your subscription has been successfully canceled'))

        # Redirecionar para a página de atualização do usuário
        return redirect('update-client')

    context = {'subscription_plan': (await subscription.aplan_choice()).name}
    return await arender(request, 'client/cancel-subscription.html', context)


@aclient_required
async def delete_account(request: HttpRequest) -> HttpResponse:
    current_user = await aget_user(request)
    try:
        subscription = await Subscription.objects.aget(user=current_user, is_active=True)
        subscription_plan_name = (await subscription.aplan_choice()).name
    except ObjectDoesNotExist:
        subscription = None
        subscription_plan_name = "No subscription"
    
    if request.method == 'POST':
        # Verificar se o usuário tem uma assinatura ativa
        try:
            if subscription:
                # Cancelar a assinatura no PayPal primeiro
                access_token = await sub_manager.get_access_token()
                sub_id = subscription.external_subscription_id
                await sub_manager.cancel_subscription(access_token, sub_id)
        except Exception:
            # Continuar mesmo se houver erro no PayPal
            pass
            
        # Adiciona mensagem antes de deletar o usuário
        await add_message(request, messages.INFO, _('Your account has been successfully deleted'))
            
        # Deletar o usuário (e consequentemente suas assinaturas devido ao CASCADE)
        await current_user.adelete()
        return redirect('home')
        
    context = {'user': current_user, 'subscription_plan': subscription_plan_name if subscription else "No subscription"}
    return await arender(request, 'client/delete-account.html', context)

@aclient_required
async def update_password(request: HttpRequest) -> HttpResponse:
    user = await aget_user(request)
    
    try:
        subscription = await Subscription.objects.aget(user=user, is_active=True)
        subscription_plan = (await subscription.aplan_choice()).name
    except ObjectDoesNotExist:
        subscription_plan = "No subscription"

    if request.method == 'POST':
        form = CustomPasswordChangeForm(user, request.POST)
        if await form.ais_valid():
            user = await form.asave()
            # Usar a versão assíncrona da função
            await async_update_session_auth_hash(request, user)
            
            # Adiciona mensagem de sucesso
            await add_message(request, messages.SUCCESS, _('Your password has been updated successfully'))
            
            # Desloga o usuário
            await alogout(request)
            
            # Redireciona para a página inicial
            return redirect('home')
        else:
            # Se o formulário não for válido, adiciona mensagem de erro
            await add_message(request, messages.ERROR, _('Please correct the errors below'))
    else:
        form = CustomPasswordChangeForm(user)
    
    context = {
        'password_form': form,
        'subscription_plan': subscription_plan,
    }
    return await arender(request, 'client/update-password.html', context)