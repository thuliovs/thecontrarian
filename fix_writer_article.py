#!/usr/bin/env python3
"""
Script para criar a tabela writer_article no banco de dados MySQL
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

def create_writer_article_table():
    """Cria a tabela writer_article se ela não existir"""
    try:
        conn = get_mysql_connection()
        if not conn:
            print("Não foi possível conectar ao banco de dados MySQL.")
            return False
        
        with conn.cursor() as cursor:
            # Verificar se a tabela existe
            cursor.execute("SHOW TABLES LIKE 'writer_article'")
            if cursor.fetchone():
                print("Tabela writer_article já existe.")
                conn.close()
                return True
            
            # Criar a tabela writer_article
            create_table_sql = """
            CREATE TABLE writer_article (
                id INT AUTO_INCREMENT PRIMARY KEY,
                writer_id INT NOT NULL,
                article_id INT NOT NULL,
                created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """
            
            print("Criando tabela writer_article...")
            cursor.execute(create_table_sql)
            conn.commit()
            print("✅ Tabela writer_article criada com sucesso!")
            
            # Adicionar índices e chaves estrangeiras separadamente
            try:
                # Adicionar índice único
                cursor.execute("ALTER TABLE writer_article ADD UNIQUE KEY writer_article_unique (writer_id, article_id)")
                conn.commit()
                print("✅ Índice único adicionado com sucesso!")
            except Exception as e:
                print(f"⚠️ Erro ao adicionar índice único: {e}")
            
            conn.close()
            return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela writer_article: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Criando tabela writer_article ===")
    if create_writer_article_table():
        print("✅ Operação concluída com sucesso!")
        sys.exit(0)
    else:
        print("❌ Ocorreram erros durante a operação.")
        sys.exit(1) 