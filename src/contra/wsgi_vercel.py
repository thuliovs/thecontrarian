"""
WSGI config para deploy no Vercel.
Configurado para usar PyMySQL e o Django completo.
"""

import os
import sys
import pymysql

# Configura PyMySQL como driver MySQL para Django
pymysql.install_as_MySQLdb()

# Adicionar o diretório src ao PATH para que o Python encontre os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura as variáveis de ambiente do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')

# Debug para mostrar variáveis importantes
print("===== DEBUG VERCEL =====")
print(f"Python Path: {sys.path}")
print(f"Current Directory: {os.getcwd()}")

try:
    from django.core.wsgi import get_wsgi_application
    app = application = get_wsgi_application()
    print("Django carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar Django: {e}")
    
    # Se falhar, exibe uma página de erro
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        
        html = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Erro de Configuração - The Contrarian Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .error {{ background-color: #f8d7da; padding: 20px; border-radius: 5px; }}
                    h1 {{ color: #721c24; }}
                </style>
            </head>
            <body>
                <h1>The Contrarian Report</h1>
                <div class="error">
                    <h2>Erro de Configuração</h2>
                    <p>Não foi possível carregar o Django:</p>
                    <pre>{str(e)}</pre>
                    <p>Por favor, entre em contato com o administrador do sistema.</p>
                </div>
            </body>
        </html>
        """
        
        return [html.encode('utf-8')] 