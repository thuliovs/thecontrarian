"""
WSGI config para deploy no Vercel.
Configurado para usar PyMySQL e o Django completo.
"""

import os
import sys
import traceback

# Importa PyMySQL antes de tudo
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("PyMySQL instalado com sucesso como MySQLdb")
except ImportError:
    print("ERRO: Não foi possível importar PyMySQL")

# Adiciona diretórios ao PYTHONPATH (vários caminhos para garantir)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)  # src
sys.path.insert(0, os.path.dirname(PROJECT_ROOT))  # raiz do projeto
sys.path.insert(0, os.getcwd())  # diretório atual

# Verificando o Python path
print("===== DIAGNÓSTICO DO AMBIENTE =====")
print(f"Python Version: {sys.version}")
print(f"Current Directory: {os.getcwd()}")
print(f"Project Root: {PROJECT_ROOT}")
print(f"Python Path: {sys.path}")
print(f"Módulos Instalados: {[m for m in sys.modules.keys() if not m.startswith('_') and '.' not in m][:10]}")
print("==================================")

# Configura variáveis de ambiente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')

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
    application = get_wsgi_application()
    app = application  # Para compatibilidade com o Vercel
    print("Django inicializado com sucesso!")
    
except Exception as e:
    print(f"Erro ao inicializar Django: {e}")
    print(traceback.format_exc())
    
    # Função de fallback para quando o Django falha
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Erro - The Contrarian Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .error {{ background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 20px; margin-top: 20px; }}
                    h1 {{ color: #343a40; }}
                    h2 {{ color: #721c24; }}
                    pre {{ background-color: #f8f9fa; padding: 10px; overflow: auto; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>The Contrarian Report</h1>
                <div class="error">
                    <h2>Erro ao inicializar o Django</h2>
                    <p>Ocorreu um erro ao tentar inicializar a aplicação Django:</p>
                    <pre>{traceback.format_exc()}</pre>
                </div>
            </body>
        </html>
        """
        
        return [error_html.encode('utf-8')] 