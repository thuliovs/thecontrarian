from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.utils.translation import gettext as _

from .django_utils import alogout, add_message

async def custom_logout(request: HttpRequest) -> HttpResponse:
    """
    Custom logout view that ensures complete session termination
    
    This function:
    1. Adds a success message to inform the user
    2. Performs a complete logout using the enhanced alogout function
    3. Sets a secure redirect with cache control headers
    4. Returns to the home page with a fresh session
    """
    # Adiciona mensagem de sucesso antes de fazer logout
    await add_message(request, messages.INFO, _('You have been successfully logged out'))
    
    # Faz o logout completo
    await alogout(request)
    
    # Cria uma resposta de redirecionamento para a página inicial
    response = redirect('home')
    
    # Adiciona headers de segurança para evitar caching da página após logout
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response 