"""
Common Django utils used by several other packages and
apps inside of this project.
"""

__all__ = (
    'AsyncFormMixin',
    'AsyncModelFormMixin',
    'AsyncViewT',
    'arender',
    'alogout',
)

from typing import Protocol

from django import forms

from asgiref.sync import sync_to_async
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

import django.contrib.auth as auth
from django.contrib import messages

class AsyncViewT(Protocol):
    async def __call__(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        ...



class AsyncFormMixin():
    @sync_to_async
    def ais_valid(self: forms.BaseForm): # type: ignore
        return self.is_valid()
    
    @sync_to_async
    def arender(self: forms.BaseForm): # type: ignore
        return self.render()
    

class AsyncModelFormMixin(AsyncFormMixin):
    async def asave(self: forms.ModelForm, *args, **kwargs): # type: ignore
        @sync_to_async
        def sync_call_save():
            return self.save(*args, **kwargs)
        return await sync_call_save()

async def arender(*render_args, **render_kargs) -> HttpResponse:
    @sync_to_async
    def sync_call_render() -> HttpResponse:
        return render(*render_args, **render_kargs)
    return await sync_call_render()

async def alogout(request, *args, **kwargs):
    """
    Versão assíncrona da função logout que garante a remoção completa dos tokens de sessão.
    
    Esta função:
    1. Executa o logout padrão do Django
    2. Limpa explicitamente o cookie de sessão
    3. Invalida a sessão atual
    4. Cria uma nova sessão vazia para evitar erros
    """
    @sync_to_async
    def sync_call_logout():
        # Logout padrão do Django
        auth.logout(request, *args, **kwargs)
        
        # Limpar explicitamente o cookie de sessão
        if hasattr(request, 'session'):
            request.session.flush()  # Remove todos os dados da sessão
            
            # Definir o cookie de sessão para expirar imediatamente
            request.session.set_expiry(-1)
            
            # Forçar a remoção do cookie de sessão
            request.session.delete()
            
            # Criar uma nova sessão vazia para evitar erros
            request.session.create()
    
    await sync_call_logout()

async def add_message(request, level, message, extra_tags=''):
    @sync_to_async
    def sync_add_message():
        messages.add_message(request, level, message, extra_tags=extra_tags)
    await sync_add_message()