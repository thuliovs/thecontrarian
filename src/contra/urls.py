"""
URL configuration for contra project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.http import HttpResponse

import account.views
from common.views import custom_logout

# Importar a view de diagnóstico
from .views import diagnose_db

# View de fallback para a home page para caso as outras rotas falhem
def home_fallback(request):
    try:
        return render(request, 'account/home.html')
    except Exception as e:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>The Contrarian Report</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; }}
                .navbar {{ background-color: #343a40 !important; }}
                .navbar-brand, .nav-link {{ color: white !important; }}
                .general-container {{ background: white; padding: 2rem; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-top: 2rem; }}
                .btn-success {{ background-color: #28a745; }}
                footer {{ text-align: center; margin-top: 3rem; padding: 1rem; color: #6c757d; }}
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container">
                    <a class="navbar-brand" href="/">The Contrarian Report</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item">
                                <a class="nav-link" href="/register">Register</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="/login">Login</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>

            <div class="container">
                <div class="general-container">
                    <div class="text-center">
                        <h5>Get access to unique and profitable perspectives on the capital markets!</h5>
                        <p class="mb-4">Access our exclusive collection of reports and articles.</p>
                        <a class="btn btn-success" style="width: 200px;" href="/register">
                            <i class="fa fa-angle-right" aria-hidden="true"></i> Get Started
                        </a>
                    </div>
                </div>
            </div>

            <footer>
                <div class="container">
                    <p>&copy; 2024 The Contrarian Report. Todos os direitos reservados.</p>
                </div>
            </footer>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
        return HttpResponse(html)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('client/', include('client.urls')),
    path('writer/', include('writer.urls')),
    path('db-diagnose/', diagnose_db, name='db_diagnose'),  # URL para diagnóstico do banco
    path('admin/diagnose-db/', diagnose_db, name='diagnose_db'),
    path('', include('contra.main_urls')),  # Incluir as URLs principais
]
