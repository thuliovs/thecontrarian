#!/usr/bin/env python
"""
Script para corrigir o banco de dados MySQL no Vercel.
Este script verifica e cria todas as tabelas e colunas necessárias para o funcionamento
adequado do The Contrarian Report.
"""

import os
import sys
import json
import traceback
from pathlib import Path

# Configurar o ambiente Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / 'src'))

# Forçar o uso do MySQL
os.environ['USE_MYSQL'] = 'True'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.contra.settings')

# Importar PyMySQL
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    print("PyMySQL instalado com sucesso como MySQLdb")
except ImportError:
    print("ERRO: Não foi possível importar PyMySQL")
    sys.exit(1)

# Definições de colunas conhecidas
KNOWN_COLUMNS = {
    "client_subscription": [
        {"name": "id", "definition": "INT AUTO_INCREMENT PRIMARY KEY"},
        {"name": "client_id", "definition": "INT NOT NULL"},
        {"name": "plan_choice_id", "definition": "INT NULL"},
        {"name": "plan", "definition": "VARCHAR(255) NULL"},
        {"name": "external_subscription_id", "definition": "VARCHAR(255) NULL"},
        {"name": "date_added", "definition": "DATETIME NULL DEFAULT CURRENT_TIMESTAMP"},
        {"name": "is_active", "definition": "BOOLEAN NULL DEFAULT 1"},
        {"name": "last_payment_date", "definition": "DATETIME NULL"},
        {"name": "next_payment_date", "definition": "DATETIME NULL"}
    ],
    "client_planchoice": [
        {"name": "id", "definition": "INT AUTO_INCREMENT PRIMARY KEY"},
        {"name": "name", "definition": "VARCHAR(255) NULL"},
        {"name": "description", "definition": "TEXT NULL"},
        {"name": "price", "definition": "DECIMAL(10,2) NULL"},
        {"name": "is_active", "definition": "BOOLEAN NULL DEFAULT 1"},
        {"name": "plan", "definition": "VARCHAR(255) NULL"}
    ],
    "django_session": [
        {"name": "session_key", "definition": "VARCHAR(40) NOT NULL PRIMARY KEY"},
        {"name": "session_data", "definition": "LONGTEXT NOT NULL"},
        {"name": "expire_date", "definition": "DATETIME(6) NOT NULL"},
    ],
    "writer_article": [
        {"name": "id", "definition": "INT AUTO_INCREMENT PRIMARY KEY"},
        {"name": "title", "definition": "VARCHAR(255) NOT NULL"},
        {"name": "content", "definition": "LONGTEXT NOT NULL"},
        {"name": "is_premium", "definition": "BOOLEAN NOT NULL DEFAULT 0"},
        {"name": "date_posted", "definition": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"},
        {"name": "user_id", "definition": "INT NOT NULL"}
    ]
}

def get_mysql_connection():
    """Conecta ao banco de dados MySQL"""
    db_name = os.environ.get('MYSQL_DATABASE', None)
    db_user = os.environ.get('MYSQL_USER', None)
    db_host = os.environ.get('MYSQL_HOST', None)
    db_password = os.environ.get('MYSQL_PASSWORD', '')
    db_port = os.environ.get('MYSQL_PORT', '3306')
    
    if not all([db_name, db_user, db_host]):
        print("ERRO: Variáveis de ambiente MySQL não configuradas!")
        return None
    
    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=int(db_port)
        )
        print(f"Conexão com MySQL estabelecida com sucesso: {db_host}/{db_name}")
        return conn
    except Exception as e:
        print(f"ERRO ao conectar ao MySQL: {e}")
        return None

def create_table_if_missing(conn, table_name, columns):
    """Cria uma tabela se ela não existir"""
    try:
        with conn.cursor() as cursor:
            # Verificar se a tabela já existe
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if cursor.fetchone():
                print(f"Tabela {table_name} já existe.")
                return True
            
            # Criar a tabela
            print(f"Criando tabela {table_name}...")
            
            column_defs = []
            for col in columns:
                column_defs.append(f"`{col['name']}` {col['definition']}")
            
            # Criar a tabela
            create_table_sql = f"""
            CREATE TABLE `{table_name}` (
                {', '.join(column_defs)}
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
            print(f"Tabela {table_name} criada com sucesso!")
            return True
    except Exception as e:
        print(f"ERRO ao criar tabela {table_name}: {e}")
        return False

def add_column_if_missing(conn, table_name, column_name, column_definition):
    """Adiciona uma coluna à tabela se ela não existir"""
    try:
        with conn.cursor() as cursor:
            # Verificar se a coluna já existe
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE '{column_name}'")
            if cursor.fetchone():
                print(f"Coluna {column_name} já existe na tabela {table_name}.")
                return True
            
            # Adicionar a coluna
            print(f"Adicionando coluna {column_name} à tabela {table_name}...")
            cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {column_definition}")
            conn.commit()
            print(f"Coluna {column_name} adicionada com sucesso à tabela {table_name}!")
            return True
    except Exception as e:
        print(f"ERRO ao adicionar coluna {column_name} à tabela {table_name}: {e}")
        return False

def fix_all_tables():
    """Verifica e corrige todas as tabelas necessárias no banco de dados."""
    try:
        conn = get_mysql_connection()
        if not conn:
            print("Não foi possível conectar ao banco de dados MySQL.")
            return False

        # Definições de tabelas - adicione aqui as tabelas que o sistema precisa
        tables = {
            # ... existing code ...
            
            # Adicionar a tabela writer_article que está faltando
            'writer_article': [
                'id INT AUTO_INCREMENT PRIMARY KEY',
                'writer_id INT NOT NULL',
                'article_id INT NOT NULL',
                'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
                'FOREIGN KEY (writer_id) REFERENCES auth_user(id) ON DELETE CASCADE',
                'FOREIGN KEY (article_id) REFERENCES articles_article(id) ON DELETE CASCADE',
                'UNIQUE KEY writer_article_unique (writer_id, article_id)'
            ],
            
            # ... existing code ...
        }

        # Criar as tabelas que não existem
        for table_name, columns in tables.items():
            create_table_if_missing(conn, table_name, columns)

        # ... existing code ...
    except Exception as e:
        print(f"ERRO ao corrigir tabelas: {e}")
        traceback.print_exc()
        return False

def extract_models_from_django():
    """Extrai os modelos do Django"""
    try:
        # Inicializar o Django
        import django
        django.setup()
        
        # Importar todos os modelos
        from django.apps import apps
        
        # Obter informações sobre os modelos
        models_info = {}
        
        for app_config in apps.get_app_configs():
            app_name = app_config.label
            if app_name in ['admin', 'auth', 'contenttypes', 'sessions', 'staticfiles']:
                continue  # Pular apps internos do Django
                
            print(f"Analisando app: {app_name}")
            models_info[app_name] = {}
            
            for model in app_config.get_models():
                model_name = model._meta.model_name
                print(f"  - Modelo: {model_name}")
                models_info[app_name][model_name] = []
                
                # Analisar campos do modelo
                for field in model._meta.fields:
                    field_info = {
                        "name": field.name,
                        "type": field.get_internal_type(),
                        "null": field.null,
                        "blank": field.blank,
                        "primary_key": field.primary_key,
                    }
                    models_info[app_name][model_name].append(field_info)
                    print(f"    - Campo: {field.name} ({field.get_internal_type()})")
        
        return models_info
    except Exception as e:
        print(f"ERRO ao extrair modelos Django: {e}")
        traceback.print_exc()
        return None

def main():
    """Função principal"""
    print("=== THE CONTRARIAN DATABASE FIXER ===")
    print(f"Diretório base: {BASE_DIR}")
    
    # Extrair modelos do Django (informativo)
    print("\n=== Extraindo modelos do Django ===")
    models_info = extract_models_from_django()
    if models_info:
        print("Extração de modelos concluída com sucesso!")
    
    # Corrigir tabelas conhecidas
    print("\n=== Corrigindo tabelas conhecidas ===")
    success = fix_all_tables()
    
    if success:
        print("\n=== RESULTADO: TODAS AS CORREÇÕES APLICADAS COM SUCESSO! ===")
    else:
        print("\n=== RESULTADO: ALGUMAS CORREÇÕES FALHARAM, VERIFIQUE OS ERROS ACIMA ===")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 