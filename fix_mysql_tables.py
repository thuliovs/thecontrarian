#!/usr/bin/env python3
"""
Script para verificar e corrigir tabelas ausentes no banco de dados MySQL
"""
import os
import sys
import pymysql
import traceback
import django
from decouple import config

# Configurar ambiente Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')
try:
    django.setup()
except Exception as e:
    print(f"Erro ao configurar Django: {e}")
    traceback.print_exc()
    sys.exit(1)

from django.conf import settings

def get_mysql_connection():
    """Obtém uma conexão com o banco de dados MySQL"""
    try:
        # Verificar se estamos usando MySQL
        if 'mysql' not in settings.DATABASES['default']['ENGINE']:
            print("Este script só funciona com MySQL")
            return None
        
        # Obter configurações do banco de dados
        db_settings = settings.DATABASES['default']
        conn = pymysql.connect(
            host=db_settings.get('HOST', 'localhost'),
            user=db_settings.get('USER', ''),
            password=db_settings.get('PASSWORD', ''),
            database=db_settings.get('NAME', ''),
            port=int(db_settings.get('PORT', 3306))
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        traceback.print_exc()
        return None

def create_table_if_missing(conn, table_name, columns):
    """Cria uma tabela se ela não existir"""
    try:
        with conn.cursor() as cursor:
            # Verificar se a tabela existe
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if cursor.fetchone():
                print(f"Tabela {table_name} já existe.")
                return True
            
            # Criar a tabela
            column_defs = ", ".join(columns)
            create_sql = f"CREATE TABLE `{table_name}` ({column_defs}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci"
            
            print(f"Criando tabela {table_name}...")
            print(create_sql)
            
            cursor.execute(create_sql)
            conn.commit()
            print(f"✅ Tabela {table_name} criada com sucesso!")
            return True
    except Exception as e:
        print(f"❌ Erro ao criar tabela {table_name}: {e}")
        traceback.print_exc()
        return False

def fix_all_tables():
    """Verifica e corrige todas as tabelas necessárias"""
    try:
        conn = get_mysql_connection()
        if not conn:
            print("Não foi possível conectar ao banco de dados MySQL.")
            return False
        
        # Lista de tabelas que devem existir
        tables = {
            # Tabela writer_article
            'writer_article': [
                'id INT AUTO_INCREMENT PRIMARY KEY',
                'writer_id INT NOT NULL',
                'article_id INT NOT NULL',
                'created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP',
                'updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
                'FOREIGN KEY (writer_id) REFERENCES auth_user(id) ON DELETE CASCADE',
                'FOREIGN KEY (article_id) REFERENCES articles_article(id) ON DELETE CASCADE',
                'UNIQUE KEY writer_article_unique (writer_id, article_id)'
            ],
            
            # Adicione outras tabelas conforme necessário
        }
        
        # Verificar e criar tabelas ausentes
        all_ok = True
        for table_name, columns in tables.items():
            if not create_table_if_missing(conn, table_name, columns):
                all_ok = False
        
        conn.close()
        return all_ok
    
    except Exception as e:
        print(f"Erro ao corrigir tabelas: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Iniciando verificação de tabelas MySQL ===")
    if fix_all_tables():
        print("✅ Todas as tabelas foram verificadas e corrigidas com sucesso!")
        sys.exit(0)
    else:
        print("❌ Ocorreram erros durante a verificação/correção de tabelas.")
        sys.exit(1) 