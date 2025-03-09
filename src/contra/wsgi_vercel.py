"""
WSGI config for Vercel deployment.
"""

import os
import sys
import traceback

# Debug para identificar o problema
print("Current directory:", os.getcwd())
print("Python path:", sys.path)
print("Contents of current directory:", os.listdir("."))
print("Contents of src directory (if exists):", os.listdir("src") if os.path.exists("src") else "src directory not found")

# Adiciona o diretório src ao path do Python de várias maneiras
# Método 1: Adiciona src ao path
sys.path.insert(0, "src")

# Método 2: Adiciona o diretório atual ao path
sys.path.insert(0, os.getcwd())

# Método 3: Adiciona os diretórios pai do arquivo atual
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')

# Set Vercel deployment environment
os.environ.setdefault('VERCEL_DEPLOYMENT', 'True')

try:
    # Somente importa o Django depois de configurar o path
    from django.core.wsgi import get_wsgi_application
    
    # Get the WSGI application
    app = get_wsgi_application()
    
    print("Django application loaded successfully!")
    
except Exception as e:
    print("Error loading Django application:", str(e))
    print("Traceback:", traceback.format_exc())
    
    # Função simples para responder em caso de erro durante o carregamento do Django
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        
        error_message = f"""
        <html>
        <head><title>Error Loading Django</title></head>
        <body>
            <h1>Error Loading Django Application</h1>
            <p>There was an error loading the Django application:</p>
            <pre>{str(e)}</pre>
            <h2>Traceback:</h2>
            <pre>{traceback.format_exc()}</pre>
            <h2>Environment:</h2>
            <pre>PYTHONPATH: {sys.path}</pre>
            <pre>Current Directory: {os.getcwd()}</pre>
            <pre>Directory Contents: {os.listdir('.')}</pre>
        </body>
        </html>
        """
        
        return [error_message.encode('utf-8')] 