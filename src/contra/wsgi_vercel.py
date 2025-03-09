"""
WSGI config para deploy no Vercel.
Configurado para usar PyMySQL e o Django completo.
"""

import os
import sys
import traceback
import json
import re
import mimetypes

# Garantir que o diretório atual esteja no PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PROJECT_DIR)  # adiciona a raiz do projeto
sys.path.insert(0, BASE_DIR)     # adiciona o diretório src
sys.path.insert(0, os.getcwd())  # adiciona o diretório atual

# Mapear tipos MIME
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("image/jpeg", ".jpeg")

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

# Verificar se estamos usando MySQL
use_mysql = os.environ.get('USE_MYSQL', 'False').lower() == 'true'
print(f"Configurado para usar MySQL: {use_mysql}")

if use_mysql:
    # Tentar verificar conexão com MySQL
    try:
        db_name = os.environ.get('MYSQL_DATABASE', 'not-set')
        db_user = os.environ.get('MYSQL_USER', 'not-set')
        db_host = os.environ.get('MYSQL_HOST', 'not-set')
        print(f"MySQL Database: {db_name}, User: {db_user}, Host: {db_host}")
        
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=os.environ.get('MYSQL_PASSWORD', ''),
            database=db_name,
            port=int(os.environ.get('MYSQL_PORT', '3306'))
        )
        print("Conexão com MySQL estabelecida com sucesso!")
        
        # Tentar verificar se a tabela account_customuser existe
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE 'account_customuser'")
                if cursor.fetchone():
                    print("Tabela account_customuser existe!")
                else:
                    print("AVISO: Tabela account_customuser não existe!")
                    print("As migrações não foram aplicadas. Verifique se as migrações foram executadas.")
        except Exception as e:
            print(f"Erro ao verificar tabela account_customuser: {e}")
        
        conn.close()
    except Exception as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        print("Verifique se as credenciais do MySQL estão corretas e o banco de dados existe.")

# Verificar arquivos estáticos disponíveis
static_dirs = [
    os.path.join(os.getcwd(), 'staticfiles_build'), 
    os.path.join(os.getcwd(), 'staticfiles_build', 'static'),
    os.path.join(os.getcwd(), 'staticfiles_build', 'css'),
    os.path.join(os.getcwd(), 'staticfiles_build', 'static', 'css')
]

print("===== ARQUIVOS ESTÁTICOS DISPONÍVEIS =====")
for static_dir in static_dirs:
    if os.path.exists(static_dir):
        print(f"Diretório: {static_dir}")
        for root, dirs, files in os.walk(static_dir):
            rel_path = os.path.relpath(root, static_dir)
            if rel_path == ".":
                rel_path = ""
            for file in files:
                print(f"  /{rel_path}/{file}" if rel_path else f"  /{file}")
    else:
        print(f"Diretório não encontrado: {static_dir}")
print("==================================")

# Configura variáveis de ambiente para o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')
os.environ['PYTHONUNBUFFERED'] = '1'  # Para garantir que os logs apareçam

# Função para servir arquivos estáticos diretamente
def serve_static_file(path, environ, start_response):
    # Procura o arquivo em vários diretórios possíveis
    search_paths = [
        os.path.join(os.getcwd(), 'staticfiles_build', path.lstrip('/')),
        os.path.join(os.getcwd(), 'staticfiles_build', 'static', path.lstrip('/')),
        os.path.join(os.getcwd(), 'staticfiles_build', path.replace('/static/', '/').lstrip('/')),
        os.path.join(os.getcwd(), path.lstrip('/'))
    ]
    
    file_path = None
    for search_path in search_paths:
        if os.path.isfile(search_path):
            file_path = search_path
            break
    
    if file_path is None:
        # Caso especial para styles.css
        if 'styles.css' in path or 'style.css' in path:
            css_paths = [
                os.path.join(os.getcwd(), 'staticfiles_build', 'css', 'styles.css'),
                os.path.join(os.getcwd(), 'staticfiles_build', 'static', 'css', 'styles.css'),
                os.path.join(os.getcwd(), 'staticfiles_build', 'css', 'style.css'),
                os.path.join(os.getcwd(), 'staticfiles_build', 'static', 'css', 'style.css')
            ]
            for css_path in css_paths:
                if os.path.isfile(css_path):
                    file_path = css_path
                    break

    if file_path is None:
        status = '404 Not Found'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [f"File not found: {path}\nSearched in: {search_paths}".encode('utf-8')]
    
    # Determinar o tipo MIME
    content_type = mimetypes.guess_type(file_path)[0] or 'text/plain'
    
    # Ler o arquivo
    with open(file_path, 'rb') as f:
        file_contents = f.read()
    
    status = '200 OK'
    headers = [
        ('Content-type', content_type),
        ('Content-Length', str(len(file_contents)))
    ]
    start_response(status, headers)
    return [file_contents]

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
        django_app = application
        
        # Verifica se conseguimos resolver a URL para a home page
        from django.urls import resolve, Resolver404
        try:
            resolve('/')
            print("URL '/' resolvida com sucesso!")
        except Resolver404:
            print("AVISO: URL '/' não pode ser resolvida - verifique as URLs")
        except Exception as e:
            print(f"Erro ao resolver URL '/': {e}")
        
        # Wrapper para servir arquivos estáticos, caso Django não os encontre
        def app(environ, start_response):
            path = environ.get('PATH_INFO', '')
            
            # Se for um arquivo estático, tenta servi-lo diretamente
            if path.startswith('/static/') or path.startswith('/css/') or path.startswith('/js/') or \
               path.endswith('.css') or path.endswith('.js'):
                print(f"Tentando servir arquivo estático: {path}")
                return serve_static_file(path, environ, start_response)
            
            # Caso contrário, passa para o Django
            try:
                return django_app(environ, start_response)
            except Exception as e:
                print(f"Erro ao processar requisição Django: {str(e)}")
                error_app = serve_error_page(f"Erro ao processar requisição: {str(e)}", traceback.format_exc())
                return error_app(environ, start_response)
            
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