"""
WSGI config para deploy no Vercel.
Configurado para usar PyMySQL e o Django completo.
"""

import os
import sys
import traceback
import json

# Garantir que o diretório atual esteja no PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PROJECT_DIR)  # adiciona a raiz do projeto
sys.path.insert(0, BASE_DIR)     # adiciona o diretório src
sys.path.insert(0, os.getcwd())  # adiciona o diretório atual

# Importa PyMySQL antes de tudo
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("PyMySQL instalado com sucesso como MySQLdb")
except ImportError:
    print("ERRO: Não foi possível importar PyMySQL")

# Diagnóstico de ambiente
print("===== DIAGNÓSTICO DO AMBIENTE =====")
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Current Directory: {os.getcwd()}")
print(f"Project Directory: {PROJECT_DIR}")
print(f"Base Directory: {BASE_DIR}")
print(f"Python Path: {sys.path}")
print(f"Environment Variables: {json.dumps({k: v for k, v in os.environ.items() if not k.startswith('PATH')})}")
print("==================================")

# Configura variáveis de ambiente para o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')
os.environ['PYTHONUNBUFFERED'] = '1'  # Para garantir que os logs apareçam

# Função para servir uma página de erro em caso de falha
def serve_error_page(error_message, traceback_info):
    def error_app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Erro - The Contrarian Report</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .error-box {{ background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        h1 {{ color: #343a40; }}
        h2 {{ color: #721c24; }}
        pre {{ background-color: #f1f1f1; padding: 10px; overflow: auto; font-size: 14px; }}
        .env {{ background-color: #e9ecef; padding: 10px; border-radius: 4px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>The Contrarian Report</h1>
        <div class="error-box">
            <h2>Erro na Inicialização</h2>
            <p><strong>Mensagem:</strong> {error_message}</p>
            <p>Ocorreu um erro ao tentar inicializar o aplicativo. Isto pode ser devido a problemas de configuração ou conexão com o banco de dados.</p>
        </div>
        
        <h3>Informações Técnicas</h3>
        <pre>{traceback_info}</pre>
        
        <div class="env">
            <h3>Ambiente</h3>
            <p><strong>Python:</strong> {sys.version}</p>
            <p><strong>PYTHONPATH:</strong> {':'.join(sys.path[:3])}...</p>
            <p><strong>Diretório Atual:</strong> {os.getcwd()}</p>
        </div>
    </div>
</body>
</html>"""
        
        return [html.encode('utf-8')]
    
    return error_app

try:
    # Tenta importar o Django
    try:
        import django
        print(f"Django versão {django.get_version()} importado com sucesso!")
    except ImportError as e:
        print(f"Falha ao importar Django: {e}")
        raise

    # Tenta obter a aplicação WSGI
    try:
        from django.core.wsgi import get_wsgi_application
        print("get_wsgi_application importado com sucesso!")
    except ImportError as e:
        print(f"Falha ao importar get_wsgi_application: {e}")
        raise

    # Inicializa o Django
    try:
        application = get_wsgi_application()
        print("Django inicializado com sucesso!")
        
        # Para compatibilidade com o Vercel
        app = application
        
        # Verifica se conseguimos resolver a URL para a home page
        from django.urls import resolve, Resolver404
        try:
            resolve('/')
            print("URL '/' resolvida com sucesso!")
        except Resolver404:
            print("AVISO: URL '/' não pode ser resolvida - verifique as URLs")
        except Exception as e:
            print(f"Erro ao resolver URL '/': {e}")
            
    except Exception as e:
        error_message = f"Erro ao inicializar aplicação Django: {str(e)}"
        print(error_message)
        print(traceback.format_exc())
        app = serve_error_page(error_message, traceback.format_exc())
        
except Exception as e:
    error_message = f"Erro não tratado: {str(e)}"
    print(error_message)
    print(traceback.format_exc())
    app = serve_error_page(error_message, traceback.format_exc()) 