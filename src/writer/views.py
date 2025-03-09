from django.http import HttpResponse, HttpRequest
from common.auth import awriter_required, aget_user, ensure_for_current_user # type: ignore
from common.django_utils import arender, add_message, alogout
from django.shortcuts import redirect
from .forms import ArticleForm, UpdateUserForm
from common.forms import CustomPasswordChangeForm
from .models import Article
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth import update_session_auth_hash
from asgiref.sync import sync_to_async  # Adicionar esta importação

# Criar uma versão assíncrona da função update_session_auth_hash
async_update_session_auth_hash = sync_to_async(update_session_auth_hash)

@awriter_required
async def dashboard(request: HttpRequest) -> HttpResponse:
    return await arender(request, 'writer/dashboard.html')

@awriter_required
async def create_article(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = await form.asave(commit = False)
            article.user = await aget_user(request)
            await article.asave()
            
            # Adicionar mensagem de sucesso
            await add_message(request, messages.SUCCESS, _('Article created successfully!'))
            
            return redirect('create-article')
    else:
        form = ArticleForm()

    context = {'create_article_form': form}
    return await arender(request, 'writer/create-article.html', context)

@awriter_required
async def my_articles(request: HttpRequest) -> HttpResponse:
    current_user = await aget_user(request)
    articles = Article.objects.filter(user=current_user)
    context = {'my_articles': articles}
    return await arender(request, 'writer/my-articles.html', context)


@awriter_required
@ensure_for_current_user(Article, redirect_if_missing = 'my-articles')
async def update_article(request: HttpRequest, article: Article) -> HttpResponse:
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance = article)
        if await form.ais_valid():
            await form.asave()
            # Adicionar mensagem de sucesso
            await add_message(request, messages.SUCCESS, _('Article updated successfully!'))
            return redirect('my-articles')
    else:
        form = ArticleForm(instance = article)

    context = {'update_article_form': form}
    return await arender(request, 'writer/update-article.html', context)

@awriter_required
@ensure_for_current_user(Article, redirect_if_missing = 'my-articles')
async def delete_article(request: HttpRequest, article: Article) -> HttpResponse:
    if request.method == 'POST':
        await article.adelete()
        # Adicionar mensagem de sucesso
        await add_message(request, messages.INFO, _('Article deleted successfully!'))
        return redirect('my-articles')
    else:
        context = {'article': article}
        return await arender(request, 'writer/delete-article.html', context)
    

@awriter_required
async def update_user(request: HttpRequest) -> HttpResponse:
    user = await aget_user(request)
    
    form = UpdateUserForm(instance=user)
    
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)
        if await form.ais_valid():
            await form.asave()
            await add_message(request, messages.SUCCESS, _('User updated successfully!'))
            return redirect('update-writer')
        else:
            await add_message(request, messages.ERROR, _('Error updating user information!'))
            form = UpdateUserForm(instance=user)
    
    context = {
        'update_user_form': form,
    }
    return await arender(request, 'writer/update-user.html', context)


@awriter_required
async def delete_account(request: HttpRequest) -> HttpResponse:
    current_user = await aget_user(request)
    if request.method == 'POST':
        # Adiciona mensagem antes de deletar o usuário
        await add_message(request, messages.INFO, _('Your account has been successfully deleted'))
        
        # Deleta o usuário
        await current_user.adelete()
        return redirect('home')
    context = {'user': current_user}
    return await arender(request, 'writer/delete-account.html', context)

@awriter_required
async def update_password(request: HttpRequest) -> HttpResponse:
    user = await aget_user(request)
    
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
    }
    return await arender(request, 'writer/update-password.html', context)