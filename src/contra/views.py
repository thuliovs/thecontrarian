"""
Views para o aplicativo principal
"""

import os
import sys
import json
import traceback
import pymysql
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

# Home fallback para quando outras rotas falham
def home_fallback(request):
    """View de fallback para a home page"""
    return render(request, 'home.html', {})

# Views de diagnóstico e correção de banco de dados
@staff_member_required
def diagnose_db(request):
    """
    View para diagnóstico e correção do banco de dados.
    Apenas acessível por membros da equipe.
    """
    # Informações sobre o ambiente
    env_info = {
        'DATABASE_ENGINE': settings.DATABASES['default']['ENGINE'],
        'DATABASE_NAME': settings.DATABASES['default']['NAME'],
        'DATABASE_HOST': settings.DATABASES.get('default', {}).get('HOST', 'localhost'),
        'USE_MYSQL': settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql',
        'DJANGO_VERSION': settings.INSTALLED_APPS,
        'VERCEL': os.environ.get('VERCEL', 'False'),
    }
    
    # Ver se é uma solicitação para corrigir o banco de dados
    fix_requested = request.GET.get('fix', 'false').lower() == 'true'
    fix_result = None
    
    # Diagnóstico do banco de dados
    db_diagnosis = {}
    tables_info = {}
    
    try:
        # Verificar se estamos usando MySQL
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.mysql':
            db_diagnosis['error'] = "Esta view só funciona com MySQL"
        else:
            # Listar tabelas e suas colunas
            db_settings = settings.DATABASES['default']
            conn = pymysql.connect(
                host=db_settings.get('HOST', 'localhost'),
                user=db_settings.get('USER', ''),
                password=db_settings.get('PASSWORD', ''),
                database=db_settings.get('NAME', ''),
                port=int(db_settings.get('PORT', 3306))
            )
            
            with conn.cursor() as cursor:
                # Listar tabelas
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                
                # Para cada tabela, listar colunas
                for table in tables:
                    cursor.execute(f"DESCRIBE `{table}`")
                    columns = cursor.fetchall()
                    tables_info[table] = [
                        {
                            'name': col[0],
                            'type': col[1],
                            'null': col[2],
                            'key': col[3],
                            'default': col[4],
                            'extra': col[5]
                        }
                        for col in columns
                    ]
            
            # Se solicitado, corrigir o banco de dados
            if fix_requested:
                # Importar e executar a verificação de banco de dados
                from contra.middleware import check_and_fix_database
                check_and_fix_database()
                fix_result = "O banco de dados foi verificado e corrigido com sucesso!"
            
            db_diagnosis['tables'] = tables_info
    except Exception as e:
        db_diagnosis['error'] = str(e)
        db_diagnosis['traceback'] = traceback.format_exc()
    
    # Verificar se é uma solicitação AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'env_info': env_info,
            'db_diagnosis': db_diagnosis,
            'fix_result': fix_result
        })
    
    # Renderizar a página
    return render(request, 'admin/diagnose_db.html', {
        'env_info': env_info,
        'db_diagnosis': db_diagnosis,
        'fix_result': fix_result,
        'json_data': json.dumps({
            'env_info': env_info,
            'db_diagnosis': db_diagnosis
        }, default=str, indent=2)
    }) 