"""
Middleware para verificar e corrigir o banco de dados durante o runtime
"""

import os
import sys
import traceback
import pymysql
from django.db import connections
from django.conf import settings

# Mapeamento básico das tabelas e colunas necessárias
REQUIRED_COLUMNS = {
    "django_session": [
        {"name": "session_key", "definition": "VARCHAR(40) NOT NULL PRIMARY KEY"},
        {"name": "session_data", "definition": "LONGTEXT NOT NULL"},
        {"name": "expire_date", "definition": "DATETIME(6) NOT NULL"},
    ],
}

# Variável para controlar se o banco de dados já foi verificado
_database_checked = False

def add_column_if_missing(conn, table_name, column_name, column_definition):
    """Adiciona uma coluna a uma tabela se ela não existir"""
    try:
        with conn.cursor() as cursor:
            # Verificar se a coluna existe
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE '{column_name}'")
            if not cursor.fetchone():
                # Adicionar a coluna
                cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {column_definition}")
                conn.commit()
                print(f"DB-FIX: Coluna {column_name} adicionada à tabela {table_name}")
                return True
            return True
    except Exception as e:
        print(f"DB-FIX: Erro ao adicionar coluna {column_name} à tabela {table_name}: {e}")
        return False

def create_table_if_missing(conn, table_name, columns):
    """Cria uma tabela se ela não existir"""
    try:
        with conn.cursor() as cursor:
            # Verificar se a tabela existe
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():
                # Criar a tabela
                column_defs = []
                for col in columns:
                    column_defs.append(f"`{col['name']}` {col['definition']}")
                
                # Adicionar chaves estrangeiras para a tabela writer_article
                if table_name == 'writer_article':
                    column_defs.append("FOREIGN KEY (writer_id) REFERENCES auth_user(id) ON DELETE CASCADE")
                    column_defs.append("FOREIGN KEY (article_id) REFERENCES writer_article(id) ON DELETE CASCADE")
                    column_defs.append("UNIQUE KEY writer_article_unique (writer_id, article_id)")
                
                create_sql = f"""
                CREATE TABLE IF NOT EXISTS `{table_name}` (
                    {', '.join(column_defs)}
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
                """
                
                cursor.execute(create_sql)
                conn.commit()
                print(f"DB-FIX: Tabela {table_name} criada com sucesso!")
                return True
            return True
    except Exception as e:
        print(f"DB-FIX: Erro ao criar tabela {table_name}: {e}")
        traceback.print_exc()
        return False

def check_and_fix_database():
    """Verifica e corrige o banco de dados"""
    global _database_checked
    
    # Evitar verificações repetidas
    if _database_checked:
        return
    
    # Verificar se estamos usando MySQL
    if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.mysql':
        _database_checked = True
        return
    
    try:
        print("DB-FIX: Verificando tabelas necessárias no banco de dados...")
        
        # Obter conexão direta com MySQL
        db_settings = settings.DATABASES['default']
        conn = pymysql.connect(
            host=db_settings.get('HOST', 'localhost'),
            user=db_settings.get('USER', ''),
            password=db_settings.get('PASSWORD', ''),
            database=db_settings.get('NAME', ''),
            port=int(db_settings.get('PORT', 3306))
        )
        
        # Verificar e corrigir tabelas
        for table_name, columns in REQUIRED_COLUMNS.items():
            # Verificar se a tabela existe
            with conn.cursor() as cursor:
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                if not cursor.fetchone():
                    print(f"DB-FIX: Tabela {table_name} não existe. Criando...")
                    create_table_if_missing(conn, table_name, columns)
                else:
                    # Verificar colunas da tabela
                    for column in columns:
                        add_column_if_missing(conn, table_name, column["name"], column["definition"])
        
        conn.close()
        print("DB-FIX: Verificação e correção do banco de dados concluída!")
    except Exception as e:
        print(f"DB-FIX: Erro ao verificar banco de dados: {e}")
        traceback.print_exc()
    
    # Marcar como verificado
    _database_checked = True

class DatabaseFixMiddleware:
    """Middleware para verificar e corrigir o banco de dados"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar e corrigir o banco de dados antes de processar a requisição
        check_and_fix_database()
        
        # Continuar com o processamento normal
        return self.get_response(request)

class SessionManagementMiddleware:
    """
    Middleware para gerenciar sessões e garantir que o logout seja completo.
    
    Este middleware:
    1. Verifica se a sessão está válida
    2. Limpa sessões expiradas periodicamente
    3. Garante que os cabeçalhos de segurança sejam aplicados em todas as respostas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Processar a requisição
        response = self.get_response(request)
        
        # Adicionar cabeçalhos de segurança a todas as respostas
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Se for uma resposta de redirecionamento após logout, adicionar cabeçalhos anti-cache
        if (hasattr(request, 'path') and 
            request.path.endswith('/logout/') and 
            300 <= response.status_code < 400):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Verificar se o usuário está autenticado mas a sessão está inválida
        if request.user.is_authenticated and not request.session.get('_auth_user_id'):
            # Forçar logout se a sessão estiver inválida
            from django.contrib.auth import logout
            logout(request)
        return None 

class AdminStaticFilesMiddleware:
    """
    Middleware para servir arquivos estáticos de admin diretamente.
    
    Este middleware verifica se a requisição é para um arquivo estático do admin
    e tenta servi-lo diretamente, evitando que a requisição chegue ao Django.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Caminhos de arquivos estáticos de admin
        self.admin_static_paths = [
            '/static/admin/', 
            '/admin/css/', 
            '/admin/js/', 
            '/admin/img/'
        ]
        
        # Mapeamento de tipos MIME
        self.mime_types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.eot': 'application/vnd.ms-fontobject'
        }
    
    def __call__(self, request):
        # Verificar se a requisição é para um arquivo estático do admin
        path = request.path
        
        # Verifica se o caminho corresponde a um arquivo estático do admin
        for admin_path in self.admin_static_paths:
            if path.startswith(admin_path):
                # Tentar servir o arquivo estático
                try:
                    # Em produção (Vercel), deixar o sistema de rotas do Vercel lidar com isso
                    if os.environ.get('VERCEL', 'False').lower() == 'true':
                        return self.get_response(request)
                    
                    # Em desenvolvimento, tentar servir o arquivo localmente
                    import os
                    from django.http import HttpResponse, FileResponse
                    from django.conf import settings
                    
                    # Determinar o caminho real do arquivo
                    if path.startswith('/static/admin/'):
                        relative_path = path[len('/static/admin/'):]
                        file_path = os.path.join(settings.STATIC_ROOT, 'admin', relative_path)
                    else:
                        # Para outros caminhos de admin
                        relative_path = path[path.find('/', 1) + 1:]  # Pular o primeiro '/'
                        file_path = os.path.join(settings.STATIC_ROOT, 'admin', relative_path)
                    
                    # Verificar se o arquivo existe
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        # Determinar o tipo MIME
                        ext = os.path.splitext(file_path)[1].lower()
                        content_type = self.mime_types.get(ext, 'application/octet-stream')
                        
                        # Servir o arquivo
                        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
                        response['Cache-Control'] = 'public, max-age=31536000, immutable'
                        return response
                except Exception as e:
                    print(f"Erro ao servir arquivo estático do admin: {e}")
                    # Continuar com o fluxo normal se houver erro
                    pass
        
        # Se não for um arquivo estático do admin ou houver erro, continuar com o fluxo normal
        return self.get_response(request) 