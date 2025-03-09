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
    
    # Pasta para armazenar os arquivos de exportação
    export_dir = BASE_DIR / 'data_export'
    export_dir.mkdir(exist_ok=True)
    
    # Lista todas as aplicações e modelos registrados
    for app_config in apps.get_app_configs():
        app_name = app_config.name
        
        # Pula aplicações internas do Django
        if app_name.startswith('django.') or app_name in ['corsheaders', 'rest_framework']:
            continue
        
        print(f"Exportando aplicação: {app_name}")
        
        # Cria um diretório para a aplicação
        app_dir = export_dir / app_name
        app_dir.mkdir(exist_ok=True)
        
        # Exporta dados para cada modelo na aplicação
        for model in app_config.get_models():
            model_name = model.__name__
            output_file = app_dir / f"{model_name}.json"
            
            # Usa dumpdata para exportar os dados
            try:
                with open(output_file, 'w') as f:
                    call_command('dumpdata', f"{app_name}.{model_name}", indent=4, stdout=f)
                print(f"  - Exportado {model_name} para {output_file}")
            except Exception as e:
                print(f"  - Erro ao exportar {model_name}: {e}")
    
    print("Exportação concluída.")
    return export_dir

def import_to_mysql(export_dir):
    """Importa os dados dos arquivos JSON para o MySQL"""
    print("Importando dados para o MySQL...")
    
    # Altera a configuração para usar MySQL
    os.environ['USE_MYSQL'] = 'True'
    
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