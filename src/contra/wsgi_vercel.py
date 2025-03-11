#!/usr/bin/env python
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
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("image/x-icon", ".ico")
mimetypes.add_type("font/woff", ".woff")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/ttf", ".ttf")
mimetypes.add_type("application/vnd.ms-fontobject", ".eot")

# Adicionar padrões para arquivos estáticos do admin
ADMIN_STATIC_PATTERNS = [
    '/static/admin/',
    '/admin/css/',
    '/admin/js/',
    '/admin/img/'
]

# Diretórios para procurar arquivos estáticos do admin
ADMIN_STATIC_DIRS = [
    os.path.join(os.getcwd(), 'staticfiles_build', 'static', 'admin'),
    os.path.join(os.getcwd(), 'staticfiles_build', 'admin'),
    os.path.join(BASE_DIR, 'static', 'admin'),
    os.path.join(PROJECT_DIR, 'staticfiles_build', 'static', 'admin'),
]

# Verificar e mostrar diretórios de arquivos estáticos do admin disponíveis
print("Verificando diretórios de arquivos estáticos do admin...")
for directory in ADMIN_STATIC_DIRS:
    if os.path.exists(directory):
        print(f"Diretório de admin disponível: {directory}")
        # Listar alguns arquivos para diagnóstico
        try:
            files = os.listdir(directory)
            print(f"  Arquivos encontrados: {len(files)} ({', '.join(files[:5])}{'...' if len(files) > 5 else ''})")
        except Exception as e:
            print(f"  Erro ao listar arquivos: {e}")
    else:
        print(f"Diretório de admin não encontrado: {directory}")

# Importa PyMySQL antes de tudo
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("PyMySQL instalado com sucesso como MySQLdb")
except ImportError:
    print("ERRO: Não foi possível importar PyMySQL")

# Forçar o uso de MySQL se estiver no Vercel
if os.environ.get('VERCEL', 'False').lower() == 'true':
    print("Ambiente Vercel detectado. Forçando USE_MYSQL=True")
    os.environ['USE_MYSQL'] = 'True'

# Variáveis para controle de estado
use_mysql = os.environ.get('USE_MYSQL', 'False').lower() == 'true'
tables_created = False
_migrations_applied = False

# Diagnóstico de ambiente
print("===== DIAGNÓSTICO DO AMBIENTE =====")
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Current Directory: {os.getcwd()}")
print(f"Project Directory: {PROJECT_DIR}")
print(f"Base Directory: {BASE_DIR}")
print(f"Python Path: {sys.path}")
print(f"Environment Variables: {json.dumps({k: v for k, v in os.environ.items() if not k.startswith('PATH')})}")
print(f"Configurado para usar MySQL: {use_mysql}")

# Função para servir arquivos estáticos diretamente
def serve_static_file(environ, start_response, path):
    """Serve um arquivo estático"""
    # Primeiro, verificar se é um arquivo estático do admin
    is_admin_file = False
    admin_relative_path = None
    
    # Verificar se o caminho corresponde a um padrão de arquivo estático do admin
    for pattern in ADMIN_STATIC_PATTERNS:
        if path.startswith(pattern):
            is_admin_file = True
            if pattern == '/static/admin/':
                admin_relative_path = path[len('/static/admin/'):]
            else:
                admin_relative_path = path[path.find('/', 1) + 1:]  # Pular o primeiro '/'
            break
    
    # Se for um arquivo do admin, procurar nos diretórios específicos de admin
    if is_admin_file and admin_relative_path:
        for admin_dir in ADMIN_STATIC_DIRS:
            admin_file_path = os.path.join(admin_dir, admin_relative_path)
            if os.path.isfile(admin_file_path):
                # Determinamos o tipo MIME
                content_type = mimetypes.guess_type(admin_file_path)[0] or 'text/plain'
                
                # Ler o arquivo
                try:
                    with open(admin_file_path, 'rb') as f:
                        file_contents = f.read()
                    
                    # Definir cabeçalhos para cache de longo prazo
                    status = '200 OK'
                    headers = [
                        ('Content-type', content_type),
                        ('Content-Length', str(len(file_contents))),
                        ('Cache-Control', 'public, max-age=31536000, immutable')
                    ]
                    start_response(status, headers)
                    print(f"Servindo arquivo de admin: {admin_file_path} ({len(file_contents)} bytes)")
                    return [file_contents]
                except Exception as e:
                    print(f"Erro ao ler arquivo de admin {admin_file_path}: {e}")
                    # Continuar para os caminhos padrão
    
    # Caminhos padrão para arquivos estáticos não-admin
    search_paths = [
        os.path.join(os.getcwd(), 'staticfiles_build', path.lstrip('/')),
        os.path.join(os.getcwd(), 'staticfiles_build', 'static', path.lstrip('/')),
        os.path.join(BASE_DIR, 'static', path.lstrip('/')),
        os.path.join(PROJECT_DIR, 'staticfiles_build', path.lstrip('/')),
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

# Configura variáveis de ambiente para o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')
os.environ['PYTHONUNBUFFERED'] = '1'  # Para garantir que os logs apareçam

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
        
        # Wrapper para servir arquivos estáticos, caso Django não os encontre
        def app(environ, start_response):
            path = environ.get('PATH_INFO', '')
            
            # Verificar se é uma solicitação para limpar o banco de dados
            if path == '/db/reset' and use_mysql:
                # Exibir apenas uma página informativa por enquanto
                status = '200 OK'
                headers = [('Content-type', 'text/html; charset=utf-8')]
                start_response(status, headers)
                
                response = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Database Reset - The Contrarian</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
                        .container { max-width: 800px; margin: 0 auto; background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
                        .info-box { background-color: #d1ecf1; padding: 15px; border-radius: 4px; margin: 20px 0; }
                        h1 { color: #343a40; }
                        a { color: #007bff; text-decoration: none; }
                        a:hover { text-decoration: underline; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>The Contrarian Report</h1>
                        <div class="info-box">
                            <h2>Funcionalidade temporariamente desativada</h2>
                            <p>A funcionalidade de reset do banco de dados foi temporariamente desativada para manutenção.</p>
                            <p>Por favor, tente novamente mais tarde.</p>
                        </div>
                        <p><a href="/">Voltar para a página principal</a></p>
                    </div>
                </body>
                </html>
                """
                
                return [response.encode('utf-8')]
                
            # Se for um arquivo estático, tenta servi-lo diretamente
            if path.startswith('/static/') or path.startswith('/css/') or path.startswith('/js/') or \
               path.startswith('/admin/') or path.startswith('/static/admin/') or \
               path.endswith('.css') or path.endswith('.js'):
                print(f"Tentando servir arquivo estático: {path}")
                return serve_static_file(environ, start_response, path)
            
            # Caso contrário, passa para o Django
            try:
                return django_app(environ, start_response)
            except Exception as e:
                error_str = str(e)
                print(f"Erro ao processar requisição Django: {error_str}")
                
                # Tentar servir arquivo estático do admin se o erro for 404 Not Found
                if "not found" in error_str.lower() and (
                   path.startswith('/admin/') or 
                   path.startswith('/static/admin/') or
                   any(ext in path.lower() for ext in ['.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.ico'])):
                    print(f"Tentando servir arquivo estático após erro 404: {path}")
                    return serve_static_file(environ, start_response, path)
                
                # Tratar erros de tabela ausente
                if "Table 'thecontrarian.writer_article' doesn't exist" in error_str:
                    try:
                        print("Criando tabela writer_article que está faltando...")
                        # Obter configurações de banco de dados
                        from django.conf import settings
                        db_settings = settings.DATABASES['default']
                        conn = pymysql.connect(
                            host=db_settings.get('HOST', 'localhost'),
                            user=db_settings.get('USER', ''),
                            password=db_settings.get('PASSWORD', ''),
                            database=db_settings.get('NAME', ''),
                            port=int(db_settings.get('PORT', 3306))
                        )
                        
                        # Criar a tabela writer_article
                        with conn.cursor() as cursor:
                            # Verificar se a tabela já existe (outra thread pode ter criado)
                            cursor.execute("SHOW TABLES LIKE 'writer_article'")
                            if not cursor.fetchone():
                                # Definição da tabela baseada na estrutura necessária
                                create_table_sql = """
                                CREATE TABLE writer_article (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    writer_id INT NOT NULL,
                                    article_id INT NOT NULL,
                                    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                    FOREIGN KEY (writer_id) REFERENCES auth_user(id) ON DELETE CASCADE,
                                    FOREIGN KEY (article_id) REFERENCES articles_article(id) ON DELETE CASCADE,
                                    UNIQUE KEY writer_article_unique (writer_id, article_id)
                                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
                                """
                                cursor.execute(create_table_sql)
                                conn.commit()
                                print("Tabela writer_article criada com sucesso!")
                            else:
                                print("Tabela writer_article já existe.")
                        
                        conn.close()
                        
                        # Tentar novamente a requisição
                        try:
                            print("Retentando requisição após criar a tabela writer_article...")
                            return django_app(environ, start_response)
                        except Exception as e2:
                            print(f"Erro após criação da tabela writer_article: {str(e2)}")
                            error_app = serve_error_page(
                                f"Erro após criação da tabela writer_article: {str(e2)}", 
                                traceback.format_exc()
                            )
                            return error_app(environ, start_response)
                    except Exception as create_error:
                        print(f"Erro ao criar tabela writer_article: {str(create_error)}")
                        traceback.print_exc()
                        error_app = serve_error_page(
                            f"Erro ao criar tabela writer_article: {str(create_error)}",
                            traceback.format_exc()
                        )
                        return error_app(environ, start_response)
                
                # Tratar erros de coluna ausente
                elif "Unknown column" in error_str:
                    try:
                        print("Tentando corrigir erro de coluna ausente...")
                        # Importar e executar a verificação de banco de dados
                        from contra.middleware import check_and_fix_database
                        check_and_fix_database()
                        
                        # Tentar novamente após a correção
                        try:
                            return django_app(environ, start_response)
                        except Exception as e2:
                            error_app = serve_error_page(
                                f"Erro após tentativa de correção: {str(e2)}", 
                                "O sistema tentou corrigir o problema, mas ocorreu outro erro."
                            )
                            return error_app(environ, start_response)
                    except Exception as fix_error:
                        error_app = serve_error_page(
                            f"Erro ao tentar corrigir banco de dados: {str(fix_error)}",
                            "Não foi possível corrigir automaticamente o problema no banco de dados."
                        )
                        return error_app(environ, start_response)
                
                # Para outros erros, mostrar página de erro padrão
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