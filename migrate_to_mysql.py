#!/usr/bin/env python
"""
Script para migrar dados do SQLite para o MySQL.
Este script:
1. Exporta todos os dados do SQLite para arquivos JSON
2. Configura o Django para usar MySQL 
3. Carrega os dados dos arquivos JSON para o MySQL
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Adiciona o diretório src ao path do Python
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / 'src'))

# Configuração para usar PyMySQL como driver MySQL
import pymysql
pymysql.install_as_MySQLdb()

# Configuração temporária para usar SQLite (source)
os.environ['USE_MYSQL'] = 'False'

# Importa o Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')

import django
django.setup()

from django.core.management import call_command
from django.apps import apps

def export_from_sqlite():
    """Exporta todos os dados do SQLite para arquivos JSON"""
    print("Exportando dados do SQLite...")
    
    # Cria diretório para os arquivos de exportação
    export_dir = BASE_DIR / 'export_data'
    export_dir.mkdir(exist_ok=True)
    
    # Lista de aplicações instaladas
    installed_apps = [app_config.label for app_config in apps.get_app_configs() 
                     if not app_config.name.startswith('django.')]
    
    # Exporta dados de cada aplicação
    for app_name in installed_apps:
        print(f"Exportando aplicação: {app_name}")
        
        # Cria diretório para a aplicação
        app_dir = export_dir / app_name
        app_dir.mkdir(exist_ok=True)
        
        # Lista de modelos da aplicação
        try:
            app_models = apps.get_app_config(app_name).get_models()
            
            for model in app_models:
                model_name = model._meta.model_name
                print(f"  - Exportando modelo: {model_name}")
                
                # Nome do arquivo de exportação
                export_file = app_dir / f"{model_name}.json"
                
                # Exporta dados usando dumpdata do Django
                try:
                    with open(export_file, 'w') as f:
                        call_command('dumpdata', f"{app_name}.{model_name}", format='json', indent=2, stdout=f)
                    
                    # Verifica se exportou algum dado
                    if export_file.stat().st_size > 0:
                        print(f"    Dados exportados para {export_file}")
                    else:
                        print(f"    Nenhum dado encontrado para {model_name}")
                except Exception as e:
                    print(f"    Erro ao exportar {model_name}: {e}")
        except Exception as e:
            print(f"  Erro ao processar aplicação {app_name}: {e}")
    
    print("Exportação concluída.")
    return export_dir

def import_to_mysql(export_dir):
    """Importa os dados dos arquivos JSON para o MySQL"""
    print("Importando dados para o MySQL...")
    
    # Altera a configuração para usar MySQL
    os.environ['USE_MYSQL'] = 'True'
    
    # Define variáveis de ambiente necessárias para o MySQL se ainda não estiverem definidas
    if 'MYSQL_HOST' not in os.environ:
        print("Definindo variáveis de ambiente para MySQL...")
        os.environ['MYSQL_HOST'] = input("MySQL Host: ")
        os.environ['MYSQL_USER'] = input("MySQL User: ")
        os.environ['MYSQL_PASSWORD'] = input("MySQL Password: ")
        os.environ['MYSQL_DATABASE'] = input("MySQL Database: ")
        os.environ['MYSQL_PORT'] = input("MySQL Port [3306]: ") or "3306"
    
    # Reinicia o Django com as novas configurações (MySQL)
    from django.db import connections
    connections.close_all()
    django.setup()
    
    # Executa as migrações no MySQL
    print("Aplicando migrações no MySQL...")
    call_command('migrate')
    
    # Percorre os arquivos de exportação e importa os dados
    for app_dir in export_dir.iterdir():
        if not app_dir.is_dir():
            continue
        
        app_name = app_dir.name
        print(f"Importando aplicação: {app_name}")
        
        for json_file in app_dir.glob('*.json'):
            model_name = json_file.stem
            print(f"  - Importando {model_name}...")
            
            try:
                # Verifica se o arquivo tem conteúdo
                if json_file.stat().st_size > 0:
                    call_command('loaddata', str(json_file))
                    print(f"    Dados importados com sucesso!")
                else:
                    print(f"    Arquivo vazio, ignorando.")
            except Exception as e:
                print(f"    Erro ao importar: {e}")
    
    print("Importação concluída.")

if __name__ == "__main__":
    # Verifica se o usuário confirma a migração
    confirm = input("Esta operação irá migrar dados do SQLite para o MySQL. Continuar? (y/n): ")
    if confirm.lower() != 'y':
        print("Operação cancelada.")
        sys.exit(0)
    
    # Exporta dados do SQLite
    export_dir = export_from_sqlite()
    
    # Importa dados para o MySQL
    import_to_mysql(export_dir)
    
    print("\nMigração concluída com sucesso!")
    print("Verifique o banco de dados MySQL para confirmar que os dados foram migrados corretamente.")
    print("Lembre-se de definir USE_MYSQL=True no seu arquivo .env para usar o MySQL por padrão.") 