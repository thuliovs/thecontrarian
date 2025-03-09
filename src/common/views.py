from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.utils.translation import gettext as _

from .django_utils import alogout, add_message

async def custom_logout(request: HttpRequest) -> HttpResponse:
    """
    Custom logout view that shows a success message
    """
    # Adiciona mensagem de sucesso antes de fazer logout
    await add_message(request, messages.INFO, _('You have been successfully logged out'))
    
    # Faz o logout
    await alogout(request)
    
    # Redireciona para a página inicial
    return redirect('home') 