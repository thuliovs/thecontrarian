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

# Forçar o uso de MySQL se estiver no Vercel
if os.environ.get('VERCEL', 'False').lower() == 'true':
    print("Ambiente Vercel detectado. Forçando USE_MYSQL=True")
    os.environ['USE_MYSQL'] = 'True'

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

# Verificar se as migrações já foram aplicadas
tables_created = False
mysql_connection_ok = False
essential_tables_exist = False

if use_mysql:
    # Tentar verificar conexão com MySQL
    try:
        db_name = os.environ.get('MYSQL_DATABASE', 'not-set')
        db_user = os.environ.get('MYSQL_USER', 'not-set')
        db_host = os.environ.get('MYSQL_HOST', 'not-set')
        db_password = os.environ.get('MYSQL_PASSWORD', '')
        db_port = os.environ.get('MYSQL_PORT', '3306')
        
        print(f"MySQL Database: {db_name}, User: {db_user}, Host: {db_host}, Port: {db_port}")
        
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=int(db_port)
        )
        mysql_connection_ok = True
        print("Conexão com MySQL estabelecida com sucesso!")
        
        # Tentar verificar se as tabelas existem
        tables_to_check = ['account_customuser', 'django_migrations', 'django_session']
        missing_tables = []
        
        try:
            with conn.cursor() as cursor:
                for table in tables_to_check:
                    cursor.execute(f"SHOW TABLES LIKE '{table}'")
                    if not cursor.fetchone():
                        missing_tables.append(table)
                
                if missing_tables:
                    print(f"Tabelas ausentes no MySQL: {', '.join(missing_tables)}")
                    print("Será necessário aplicar migrações durante o runtime.")
                    # Verificar se as tabelas essenciais existem
                    if 'django_session' not in missing_tables and 'account_customuser' not in missing_tables:
                        essential_tables_exist = True
                else:
                    print("Todas as tabelas principais existem!")
                    tables_created = True
                    essential_tables_exist = True
        except Exception as e:
            print(f"Erro ao verificar tabelas: {e}")
        
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

# Flag para controlar se as migrações já foram executadas
_migrations_applied = False

# Mapas de tabelas e colunas que podem estar ausentes no dashboard do cliente
CLIENT_DASHBOARD_TABLES = {
    "client_subscription": [
        {"name": "external_subscription_id", "definition": "VARCHAR(255) NULL"},
        {"name": "date_added", "definition": "DATETIME NULL DEFAULT CURRENT_TIMESTAMP"},
        {"name": "is_active", "definition": "BOOLEAN NULL DEFAULT 1"},
        {"name": "last_payment_date", "definition": "DATETIME NULL"},
        {"name": "next_payment_date", "definition": "DATETIME NULL"}
    ],
    "client_profile": [
        {"name": "bio", "definition": "TEXT NULL"},
        {"name": "avatar", "definition": "VARCHAR(255) NULL"},
        {"name": "company_name", "definition": "VARCHAR(255) NULL"},
        {"name": "website", "definition": "VARCHAR(255) NULL"}
    ],
    "client_payment": [
        {"name": "amount", "definition": "DECIMAL(10,2) NULL"},
        {"name": "payment_date", "definition": "DATETIME NULL"},
        {"name": "transaction_id", "definition": "VARCHAR(255) NULL"},
        {"name": "status", "definition": "VARCHAR(50) NULL"}
    ]
}

# Função para criar tabela django_session manualmente
def create_session_table():
    try:
        print("Tentando criar tabela django_session manualmente...")
        db_name = os.environ.get('MYSQL_DATABASE', 'not-set')
        db_user = os.environ.get('MYSQL_USER', 'not-set')
        db_host = os.environ.get('MYSQL_HOST', 'not-set')
        db_password = os.environ.get('MYSQL_PASSWORD', '')
        db_port = os.environ.get('MYSQL_PORT', '3306')
        
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=int(db_port)
        )
        
        with conn.cursor() as cursor:
            # Verificar se a tabela já existe
            cursor.execute("SHOW TABLES LIKE 'django_session'")
            if cursor.fetchone():
                print("Tabela django_session já existe.")
                conn.close()
                return True
            
            # Criar a tabela django_session manualmente
            cursor.execute("""
            CREATE TABLE `django_session` (
                `session_key` varchar(40) NOT NULL,
                `session_data` longtext NOT NULL,
                `expire_date` datetime(6) NOT NULL,
                PRIMARY KEY (`session_key`),
                KEY `django_session_expire_date_a5c62663` (`expire_date`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """)
            conn.commit()
            print("Tabela django_session criada com sucesso!")
            conn.close()
            return True
    except Exception as e:
        print(f"Erro ao criar tabela django_session: {e}")
        return False

# Função para adicionar coluna ausente em qualquer tabela
def add_missing_column(table_name, column_name, column_definition=None):
    try:
        print(f"Tentando adicionar coluna {column_name} à tabela {table_name}...")
        
        # Determinar o tipo de coluna baseado no nome, se não foi fornecido
        if column_definition is None:
            # Coloca nomes de coluna comuns e seus tipos
            column_types = {
                "id": "INT AUTO_INCREMENT PRIMARY KEY",
                "date": "DATETIME NULL",
                "date_added": "DATETIME NULL DEFAULT CURRENT_TIMESTAMP",
                "created_at": "DATETIME NULL DEFAULT CURRENT_TIMESTAMP",
                "updated_at": "DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
                "timestamp": "TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP",
                "email": "VARCHAR(255) NULL",
                "name": "VARCHAR(255) NULL",
                "title": "VARCHAR(255) NULL",
                "description": "TEXT NULL",
                "content": "LONGTEXT NULL",
                "price": "DECIMAL(10,2) NULL",
                "is_active": "BOOLEAN NULL DEFAULT 1",
                "status": "VARCHAR(50) NULL",
                "external_id": "VARCHAR(255) NULL",
                "external_subscription_id": "VARCHAR(255) NULL"
            }
            
            # Verificar se o nome da coluna está no dicionário
            if column_name in column_types:
                column_definition = column_types[column_name]
            # Verificar se o nome da coluna contém palavras-chave
            elif any(keyword in column_name.lower() for keyword in ["date", "time", "created", "updated"]):
                column_definition = "DATETIME NULL DEFAULT CURRENT_TIMESTAMP"
            elif any(keyword in column_name.lower() for keyword in ["id", "pk", "key", "code"]):
                column_definition = "VARCHAR(255) NULL"
            elif any(keyword in column_name.lower() for keyword in ["price", "cost", "amount", "value"]):
                column_definition = "DECIMAL(10,2) NULL"
            elif any(keyword in column_name.lower() for keyword in ["is_", "has_", "can_"]):
                column_definition = "BOOLEAN NULL DEFAULT 0"
            else:
                # Padrão para outros tipos de coluna
                column_definition = "VARCHAR(255) NULL"
        
        db_name = os.environ.get('MYSQL_DATABASE', 'not-set')
        db_user = os.environ.get('MYSQL_USER', 'not-set')
        db_host = os.environ.get('MYSQL_HOST', 'not-set')
        db_password = os.environ.get('MYSQL_PASSWORD', '')
        db_port = os.environ.get('MYSQL_PORT', '3306')
        
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=int(db_port)
        )
        
        with conn.cursor() as cursor:
            # Verificar se a tabela existe
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():
                print(f"Tabela {table_name} não existe. Migração completa é necessária.")
                conn.close()
                return False
            
            # Verificar se a coluna já existe
            cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{column_name}'")
            if cursor.fetchone():
                print(f"Coluna {column_name} já existe na tabela {table_name}.")
                conn.close()
                return True
            
            # Adicionar a coluna ausente
            print(f"Adicionando coluna {column_name} à tabela {table_name} como {column_definition}...")
            cursor.execute(f"""
            ALTER TABLE {table_name} 
            ADD COLUMN {column_name} {column_definition}
            """)
            conn.commit()
            print(f"Coluna {column_name} adicionada com sucesso à tabela {table_name}!")
            conn.close()
            return True
    except Exception as e:
        print(f"Erro ao adicionar coluna {column_name} à tabela {table_name}: {e}")
        return False

# Função para adicionar colunas ausentes na tabela client_subscription
def fix_client_subscription_table():
    # Lista de colunas que podem estar faltando em client_subscription
    columns_to_add = [
        {"name": "external_subscription_id", "definition": "VARCHAR(255) NULL"},
        {"name": "date_added", "definition": "DATETIME NULL DEFAULT CURRENT_TIMESTAMP"},
        # Adicione outras colunas que possam estar faltando
    ]
    
    success = True
    for column in columns_to_add:
        if not add_missing_column("client_subscription", column["name"], column["definition"]):
            success = False
    
    return success

# Função para corrigir problemas específicos de tabela/coluna ausente
def fix_specific_table_issues():
    # Lista de funções de correção para problemas específicos
    fix_functions = [
        create_session_table,
        fix_client_subscription_table
    ]
    
    success = True
    for fix_func in fix_functions:
        if not fix_func():
            success = False
    
    return success

# Função para verificar e corrigir todas as tabelas/colunas relacionadas ao dashboard do cliente
def fix_client_dashboard_tables():
    print("Verificando e corrigindo tabelas relacionadas ao dashboard do cliente...")
    success = True
    
    # Verificar todas as tabelas e colunas definidas no mapa
    for table_name, columns in CLIENT_DASHBOARD_TABLES.items():
        print(f"Verificando tabela {table_name}...")
        try:
            # Verificar se a tabela existe
            db_name = os.environ.get('MYSQL_DATABASE', 'not-set')
            db_user = os.environ.get('MYSQL_USER', 'not-set')
            db_host = os.environ.get('MYSQL_HOST', 'not-set')
            db_password = os.environ.get('MYSQL_PASSWORD', '')
            db_port = os.environ.get('MYSQL_PORT', '3306')
            
            conn = pymysql.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
                port=int(db_port)
            )
            
            with conn.cursor() as cursor:
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                if not cursor.fetchone():
                    print(f"Tabela {table_name} não existe. Será criada pelas migrações do Django.")
                    continue
                
                # Verificar cada coluna
                for column in columns:
                    if not add_missing_column(table_name, column["name"], column["definition"]):
                        success = False
            
            conn.close()
        except Exception as e:
            print(f"Erro ao verificar tabela {table_name}: {e}")
            success = False
    
    return success

# Função para aplicar migrações
def apply_migrations():
    global _migrations_applied, tables_created, mysql_connection_ok, essential_tables_exist
    
    if _migrations_applied:
        return True
    
    if not use_mysql:
        print("Não estamos usando MySQL, ignorando migrações.")
        _migrations_applied = True
        return True
    
    if tables_created:
        print("Tabelas já existem, ignorando migrações.")
        _migrations_applied = True
        return True
    
    if not mysql_connection_ok:
        print("Conexão com MySQL falhou, não é possível aplicar migrações.")
        return False
    
    print("====== APLICANDO MIGRAÇÕES DO DJANGO DURANTE RUNTIME ======")
    try:
        import django
        from django.core.management import execute_from_command_line
        
        # Inicializa o Django
        django.setup()
        
        # Verificar se precisamos limpar o banco de dados antes
        # Tentar conectar ao banco e verificar se há tabelas inconsistentes
        try:
            db_name = os.environ.get('MYSQL_DATABASE', 'not-set')
            db_user = os.environ.get('MYSQL_USER', 'not-set')
            db_host = os.environ.get('MYSQL_HOST', 'not-set')
            db_password = os.environ.get('MYSQL_PASSWORD', '')
            db_port = os.environ.get('MYSQL_PORT', '3306')
            
            # Tentar listar todas as tabelas
            conn = pymysql.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
                port=int(db_port)
            )
            
            with conn.cursor() as cursor:
                # Verificar se alguma tabela existe
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                if tables:
                    print(f"Banco de dados existente com {len(tables)} tabelas. Verificando estado.")
                    
                    # Verificar se django_migrations existe
                    cursor.execute("SHOW TABLES LIKE 'django_migrations'")
                    if not cursor.fetchone():
                        print("O banco de dados está em um estado inconsistente: tabelas existem mas django_migrations não.")
                        print("Tentando limpar o banco de dados antes de aplicar migrações...")
                        
                        # Limpar todas as tabelas
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                        for table in tables:
                            table_name = table[0]
                            print(f"Removendo tabela: {table_name}")
                            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                        conn.commit()
                        print("Banco de dados limpo com sucesso. Pronto para migrações.")
                    
                    # Caso específico: verificar se client_planchoice existe e tem problema com a coluna 'plan'
                    cursor.execute("SHOW TABLES LIKE 'client_planchoice'")
                    if cursor.fetchone():
                        try:
                            cursor.execute("SELECT `plan` FROM `client_planchoice` LIMIT 1")
                        except Exception as e:
                            if "Unknown column 'plan'" in str(e):
                                print("Detectado problema na tabela client_planchoice: coluna 'plan' ausente.")
                                print("Removendo tabela problemática...")
                                cursor.execute("DROP TABLE IF EXISTS `client_planchoice`")
                                conn.commit()
                                print("Tabela problemática removida.")
            
            conn.close()
        except Exception as e:
            print(f"Erro ao verificar estado do banco de dados: {e}")
            # Continuar mesmo se houver erro, pois o migrate tentará criar as tabelas
        
        # Executa migrações
        print("Executando migrações do Django...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("Migrações aplicadas com sucesso durante runtime!")
        _migrations_applied = True
        tables_created = True
        return True
    except Exception as e:
        print(f"ERRO ao aplicar migrações durante runtime: {e}")
        print(traceback.format_exc())
        
        # Tentar recuperação de erro específico: client_planchoice
        if "Unknown column 'plan' in 'client_planchoice'" in str(e):
            try:
                print("Tentando recuperação de erro específico para 'client_planchoice'...")
                
                # Conectar diretamente para remover a tabela problemática
                db_name = os.environ.get('MYSQL_DATABASE', 'not-set')
                db_user = os.environ.get('MYSQL_USER', 'not-set')
                db_host = os.environ.get('MYSQL_HOST', 'not-set')
                db_password = os.environ.get('MYSQL_PASSWORD', '')
                db_port = os.environ.get('MYSQL_PORT', '3306')
                
                conn = pymysql.connect(
                    host=db_host,
                    user=db_user,
                    password=db_password,
                    database=db_name,
                    port=int(db_port)
                )
                
                with conn.cursor() as cursor:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                    cursor.execute("DROP TABLE IF EXISTS `client_planchoice`")
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                    conn.commit()
                conn.close()
                
                print("Tabela problemática removida. Tentando migrações novamente...")
                django.setup()
                execute_from_command_line(['manage.py', 'migrate'])
                
                print("Recuperação bem-sucedida! Migrações aplicadas após correção.")
                _migrations_applied = True
                tables_created = True
                return True
            except Exception as e2:
                print(f"Falha na tentativa de recuperação: {e2}")
                return False
                
        return False

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
        
        # Se o erro é relacionado a banco de dados, adicionar informações específicas
        db_info = ""
        if use_mysql:
            db_info = f"""
            <div class="db-info">
                <h3>Informações de Banco de Dados</h3>
                <p><strong>Banco:</strong> MySQL</p>
                <p><strong>Host:</strong> {os.environ.get('MYSQL_HOST', 'não definido')}</p>
                <p><strong>Banco de dados:</strong> {os.environ.get('MYSQL_DATABASE', 'não definido')}</p>
                <p><strong>Usuário:</strong> {os.environ.get('MYSQL_USER', 'não definido')}</p>
                <p><strong>Tabelas criadas:</strong> {'Sim' if tables_created else 'Não'}</p>
            </div>
            """
        
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
        .db-info {{ background-color: #d1ecf1; padding: 10px; border-radius: 4px; margin: 20px 0; color: #0c5460; }}
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
        
        {db_info}
        
        <h3>Informações Técnicas</h3>
        <pre>{traceback_info}</pre>
        
        <div class="env">
            <h3>Ambiente</h3>
            <p><strong>Python:</strong> {sys.version}</p>
            <p><strong>PYTHONPATH:</strong> {':'.join(sys.path[:3])}...</p>
            <p><strong>Diretório Atual:</strong> {os.getcwd()}</p>
            <p><strong>USE_MYSQL:</strong> {os.environ.get('USE_MYSQL', 'não definido')}</p>
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
            
            # Verificar se é uma solicitação para limpar o banco de dados
            if path == '/db/reset' and use_mysql:
                # Tentar limpar todas as tabelas do banco de dados e reiniciar
                try:
                    db_name = os.environ.get('MYSQL_DATABASE', 'not-set')
                    db_user = os.environ.get('MYSQL_USER', 'not-set')
                    db_host = os.environ.get('MYSQL_HOST', 'not-set')
                    db_password = os.environ.get('MYSQL_PASSWORD', '')
                    db_port = os.environ.get('MYSQL_PORT', '3306')
                    
                    conn = pymysql.connect(
                        host=db_host,
                        user=db_user,
                        password=db_password,
                        database=db_name,
                        port=int(db_port)
                    )
                    
                    with conn.cursor() as cursor:
                        # Obter lista de tabelas
                        cursor.execute("SHOW TABLES")
                        tables = cursor.fetchall()
                        
                        # Desativar verificação de chaves estrangeiras temporariamente
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                        
                        # Limpar todas as tabelas
                        tables_dropped = []
                        for table in tables:
                            table_name = table[0]
                            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                            tables_dropped.append(table_name)
                        
                        # Reativar verificação de chaves estrangeiras
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                        conn.commit()
                    conn.close()
                    
                    # Redefinir flags para que migrações sejam aplicadas novamente
                    global _migrations_applied, tables_created
                    _migrations_applied = False
                    tables_created = False
                    
                    # Retornar uma página de sucesso
                    status = '200 OK'
                    headers = [('Content-type', 'text/html; charset=utf-8')]
                    start_response(status, headers)
                    
                    response = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Banco de Dados Limpo - The Contrarian</title>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                            .container {{ max-width: 800px; margin: 0 auto; background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                            .success-box {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 4px; margin: 20px 0; color: #155724; }}
                            h1 {{ color: #343a40; }}
                            ul {{ margin-top: 10px; }}
                            a {{ color: #007bff; text-decoration: none; }}
                            a:hover {{ text-decoration: underline; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>The Contrarian Report</h1>
                            <div class="success-box">
                                <h2>Banco de dados limpo com sucesso!</h2>
                                <p>Todas as tabelas foram removidas e as migrações serão aplicadas novamente quando você acessar o site.</p>
                                <p><strong>Tabelas removidas:</strong></p>
                                <ul>
                                    {"".join(f"<li>{table}</li>" for table in tables_dropped)}
                                </ul>
                            </div>
                            <p><a href="/">Voltar para a página principal</a></p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    return [response.encode('utf-8')]
                except Exception as e:
                    # Em caso de erro, mostra uma página com o erro
                    status = '500 Internal Server Error'
                    headers = [('Content-type', 'text/html; charset=utf-8')]
                    start_response(status, headers)
                    
                    error_message = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Erro - The Contrarian</title>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                            .container {{ max-width: 800px; margin: 0 auto; background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                            .error-box {{ background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 4px; margin: 20px 0; color: #721c24; }}
                            h1 {{ color: #343a40; }}
                            pre {{ background-color: #f1f1f1; padding: 10px; overflow: auto; font-size: 14px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>The Contrarian Report</h1>
                            <div class="error-box">
                                <h2>Erro ao limpar banco de dados</h2>
                                <p>Ocorreu um erro ao tentar limpar o banco de dados:</p>
                                <pre>{str(e)}</pre>
                            </div>
                            <p><a href="/">Voltar para a página principal</a></p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    return [error_message.encode('utf-8')]
            
            # Aplicar migrações, se necessário, na primeira requisição
            if not _migrations_applied and use_mysql and not tables_created:
                migrations_success = apply_migrations()
                if not migrations_success and path.startswith('/account/register/'):
                    # Se estamos tentando acessar o registro e as migrações falharam, mostrar erro específico
                    error_app = serve_error_page(
                        "Não foi possível aplicar migrações MySQL. A tabela account_customuser não existe.", 
                        "As migrações do Django precisam ser executadas para criar as tabelas necessárias."
                    )
                    return error_app(environ, start_response)
            
            # Verificar especificamente para a rota de login se a tabela de sessão existe
            if path.startswith('/account/login/'):
                # Verificar se a tabela django_session existe
                db_name = os.environ.get('MYSQL_DATABASE', 'not-set')
                db_user = os.environ.get('MYSQL_USER', 'not-set')
                db_host = os.environ.get('MYSQL_HOST', 'not-set')
                db_password = os.environ.get('MYSQL_PASSWORD', '')
                db_port = os.environ.get('MYSQL_PORT', '3306')
                
                try:
                    conn = pymysql.connect(
                        host=db_host,
                        user=db_user,
                        password=db_password,
                        database=db_name,
                        port=int(db_port)
                    )
                    
                    with conn.cursor() as cursor:
                        cursor.execute("SHOW TABLES LIKE 'django_session'")
                        if not cursor.fetchone():
                            print("Tabela django_session não existe. Tentando criar...")
                            # Tentar criar a tabela manualmente
                            if not create_session_table():
                                # Se falhar na criação manual, tentar aplicar migrações específicas
                                print("Tentando aplicar migrações específicas de sessão...")
                                import django
                                django.setup()
                                from django.core.management import execute_from_command_line
                                execute_from_command_line(['manage.py', 'migrate', 'sessions'])
                
                except Exception as e:
                    print(f"Erro ao verificar tabela django_session: {e}")
            
            # Verificar especificamente para a rota do dashboard do cliente
            if path.startswith('/client/dashboard/'):
                # Tentar corrigir problemas específicos com tabelas/colunas do dashboard
                print("Rota do dashboard do cliente detectada. Verificando tabelas específicas...")
                fix_client_dashboard_tables()
            
            # Se for um arquivo estático, tenta servi-lo diretamente
            if path.startswith('/static/') or path.startswith('/css/') or path.startswith('/js/') or \
               path.endswith('.css') or path.endswith('.js'):
                print(f"Tentando servir arquivo estático: {path}")
                return serve_static_file(path, environ, start_response)
            
            # Caso contrário, passa para o Django
            try:
                return django_app(environ, start_response)
            except Exception as e:
                error_str = str(e)
                print(f"Erro ao processar requisição Django: {error_str}")
                
                # Tratamento específico para erro de sessão
                if "Table 'thecontrarian.django_session' doesn't exist" in error_str:
                    print("Erro de tabela django_session. Tentando criar tabela e tentar novamente...")
                    session_created = create_session_table()
                    if session_created:
                        try:
                            return django_app(environ, start_response)
                        except Exception as e2:
                            error_app = serve_error_page(
                                f"Erro após criar tabela de sessão: {str(e2)}", 
                                "A tabela django_session foi criada, mas ocorreu outro erro. Tente novamente."
                            )
                            return error_app(environ, start_response)
                    else:
                        error_app = serve_error_page(
                            "Não foi possível criar a tabela django_session", 
                            f"Para resolver este problema, acesse <a href='/db/reset'>este link</a> para limpar o banco de dados e recomeçar."
                        )
                        return error_app(environ, start_response)
                # Tratamento específico para erro de coluna ausente em client_subscription
                elif "Unknown column 'client_subscription.external_subscription_id'" in error_str:
                    print("Erro de coluna ausente em client_subscription. Tentando corrigir...")
                    column_fixed = fix_client_subscription_table()
                    if column_fixed:
                        try:
                            return django_app(environ, start_response)
                        except Exception as e2:
                            error_app = serve_error_page(
                                f"Erro após adicionar coluna à tabela: {str(e2)}", 
                                "A coluna external_subscription_id foi adicionada à tabela client_subscription, mas ocorreu outro erro. Tente novamente."
                            )
                            return error_app(environ, start_response)
                    else:
                        error_app = serve_error_page(
                            "Não foi possível adicionar a coluna à tabela client_subscription", 
                            f"Para resolver este problema, acesse <a href='/db/reset'>este link</a> para limpar o banco de dados e recomeçar."
                        )
                        return error_app(environ, start_response)
                # Tratamento genérico para erros de coluna ausente em qualquer tabela
                elif "Unknown column" in error_str and "in 'field list'" in error_str:
                    # Extrair o nome da tabela e da coluna do erro
                    match = re.search(r"Unknown column '([^']+)\.([^']+)' in", error_str)
                    if match:
                        table_name = match.group(1)
                        column_name = match.group(2)
                        print(f"Erro de coluna ausente: {column_name} na tabela {table_name}. Tentando corrigir...")
                        column_fixed = add_missing_column(table_name, column_name)
                        if column_fixed:
                            try:
                                return django_app(environ, start_response)
                            except Exception as e2:
                                error_app = serve_error_page(
                                    f"Erro após adicionar coluna à tabela: {str(e2)}", 
                                    f"A coluna {column_name} foi adicionada à tabela {table_name}, mas ocorreu outro erro. Tente novamente."
                                )
                                return error_app(environ, start_response)
                        else:
                            error_app = serve_error_page(
                                f"Não foi possível adicionar a coluna {column_name} à tabela {table_name}", 
                                f"Para resolver este problema, acesse <a href='/db/reset'>este link</a> para limpar o banco de dados e recomeçar."
                            )
                            return error_app(environ, start_response)
                # Tratamento para outras tabelas ausentes
                elif "Table" in error_str and "doesn't exist" in error_str and not _migrations_applied:
                    print("Erro relacionado a tabela inexistente. Tentando aplicar migrações...")
                    migrations_success = apply_migrations()
                    if migrations_success:
                        # Se as migrações foram aplicadas com sucesso, tentar novamente
                        try:
                            return django_app(environ, start_response)
                        except Exception as e2:
                            error_app = serve_error_page(f"Erro após migrações: {str(e2)}", traceback.format_exc())
                            return error_app(environ, start_response)
                    else:
                        error_app = serve_error_page(
                            f"Falha ao aplicar migrações: {str(e)}", 
                            f"Erro durante migrações. Para resolver, tente acessar <a href='/db/reset'>este link</a> para limpar o banco de dados."
                        )
                        return error_app(environ, start_response)
                else:
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