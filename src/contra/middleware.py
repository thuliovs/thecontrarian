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
    ]
}

# Flag para controlar se as verificações já foram executadas
_database_checked = False

def add_column_if_missing(conn, table_name, column_name, column_definition):
    """Adiciona uma coluna à tabela se ela não existir"""
    try:
        with conn.cursor() as cursor:
            # Verificar se a coluna já existe
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE '{column_name}'")
            if cursor.fetchone():
                return True  # Coluna já existe
            
            # Adicionar a coluna
            print(f"DB-FIX: Adicionando coluna {column_name} à tabela {table_name}...")
            cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {column_definition}")
            conn.commit()
            print(f"DB-FIX: Coluna {column_name} adicionada com sucesso à tabela {table_name}!")
            return True
    except Exception as e:
        print(f"DB-FIX: ERRO ao adicionar coluna {column_name} à tabela {table_name}: {e}")
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
                    print(f"DB-FIX: Tabela {table_name} não existe. Será criada via migração padrão.")
                    continue
                
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