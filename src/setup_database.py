#!/usr/bin/env python
"""
Script para configurar o banco de dados com as tabelas necessárias
e aplicar as migrações do Django.
"""

import os
import sys
import django
from django.db import connection
from django.core.management import call_command

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')
django.setup()

def setup_database():
    """
    Configura o banco de dados executando o SQL e as migrações
    """
    print("Iniciando configuração do banco de dados...")
    
    # Primeiro, aplicar as migrações do Django
    print("\n1. Aplicando migrações do Django...")
    call_command('migrate')
    
    # Depois, executar o script SQL personalizado
    print("\n2. Executando script SQL personalizado...")
    sql_file_path = os.path.join(os.path.dirname(__file__), 'setup_database.sql')
    
    try:
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
            
        with connection.cursor() as cursor:
            # Dividir o script em comandos individuais
            sql_commands = sql_script.split(';')
            
            for command in sql_commands:
                # Ignorar linhas vazias ou comentários
                if command.strip() and not command.strip().startswith('--'):
                    try:
                        cursor.execute(command)
                        print("Comando SQL executado com sucesso.")
                    except Exception as e:
                        print(f"Erro ao executar comando SQL: {str(e)}")
                        print(f"Comando: {command}")
                        # Continuar mesmo se houver erro, pois pode ser que a tabela já exista
                        continue
        
        print("\nConfigurações do banco de dados concluídas com sucesso!")
        
    except Exception as e:
        print(f"\nErro durante a configuração do banco de dados: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    setup_database() 