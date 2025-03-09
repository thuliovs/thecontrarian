#!/bin/bash

# Script para compilar os arquivos estáticos para o deploy no Vercel
echo "===== Starting static files build process ====="
echo "Current directory: $(pwd)"
echo "Directory listing:"
ls -la
echo "===== Environment information ====="
echo "Node version: $(node --version 2>&1 || echo 'Node not found')"
echo "Python versions:"
python --version 2>&1 || echo "Python não encontrado"
python3 --version 2>&1 || echo "Python3 não encontrado"
python3.9 --version 2>&1 || echo "Python3.9 não encontrado"

echo "===== Creating static directories ====="

# Cria pasta para arquivos estáticos - vamos pular a parte de collectstatic
echo "Criando estrutura de arquivos estáticos manualmente (sem depender do collectstatic)"
mkdir -p staticfiles_build/static
mkdir -p staticfiles_build/css
mkdir -p staticfiles_build/js
mkdir -p staticfiles_build/img

# Copiar o arquivo CSS original do projeto (se existir)
if [ -f src/static/css/styles.css ]; then
    echo "Copiando arquivo CSS original (styles.css)"
    cp src/static/css/styles.css staticfiles_build/css/
    echo "Arquivo CSS original copiado com sucesso"
else
    echo "Arquivo CSS original não encontrado, criando versão básica"
    # Criando arquivo CSS básico como fallback
    echo "/* Base CSS file for The Contrarian Report */" > staticfiles_build/css/styles.css
    echo "body{font-family:sans-serif;line-height:1.6;margin:0;padding:0;background:#f8f9fa}.navbar{background:#343a40;padding:1rem}.navbar-brand,.nav-link{color:#fff!important}.general-container{background:#fff;padding:2rem;border-radius:5px;box-shadow:0 2px 10px rgba(0,0,0,0.1);max-width:1140px;margin:2rem auto}.btn-success{background:#28a745;border-color:#28a745}.text-center{text-align:center}footer{text-align:center;padding:2rem 0;color:#6c757d}" >> staticfiles_build/css/styles.css
fi

# Também criamos o style.css (singular) para compatibilidade com possíveis referências
cp staticfiles_build/css/styles.css staticfiles_build/css/style.css

# Criando arquivo JS básico
echo "// Base JavaScript file for The Contrarian Report" > staticfiles_build/js/main.js

# Criando arquivo CSS específico para o Vercel
echo "/* Vercel deployment CSS */" > staticfiles_build/static/vercel.css

# Criar cópias na pasta /static/css para garantir compatibilidade com diferentes caminhos
mkdir -p staticfiles_build/static/css
cp staticfiles_build/css/styles.css staticfiles_build/static/css/
cp staticfiles_build/css/style.css staticfiles_build/static/css/

# Determinar o interpretador Python disponível
if command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Não foi possível encontrar um interpretador Python"
    PYTHON_CMD=""
fi

# Verificar se vamos usar MySQL ou SQLite
USE_MYSQL=$(grep -q "\"USE_MYSQL\": \"True\"" vercel.json && echo "True" || echo "False")
echo "USE_MYSQL: $USE_MYSQL"

if [ "$USE_MYSQL" == "True" ]; then
    echo "===== Configurando para usar MySQL ====="
    
    if [ -n "$PYTHON_CMD" ]; then
        # Criar um script para executar migrações no MySQL
        echo "Criando script para executar migrações no MySQL..."
        cd src || echo "Não foi possível mudar para o diretório src"
        
        cat > run_mysql_migrations.py << 'EOF'
#!/usr/bin/env python

import os
import sys
import django

# Garantir que vamos usar MySQL
os.environ['USE_MYSQL'] = 'True'

# Configurar o ambiente do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
django.setup()

# Verificar a conexão com o banco de dados
from django.db import connections
try:
    conn = connections['default']
    conn.cursor()
    print("Conexão com o MySQL estabelecida com sucesso!")
except Exception as e:
    print(f"Erro ao conectar ao MySQL: {e}")
    sys.exit(1)

# Executar migrações
from django.core.management import execute_from_command_line

print("Executando migrações do Django para MySQL...")
execute_from_command_line(['manage.py', 'migrate'])
print("Migrações MySQL concluídas.")
EOF
        
        # Executar o script de migrações MySQL
        echo "Executando migrações para MySQL..."
        $PYTHON_CMD run_mysql_migrations.py || echo "Falha ao executar migrações para MySQL"
        cd ..
    else
        echo "Não foi possível executar migrações para MySQL: Python não encontrado"
    fi
else
    echo "===== Configurando para usar SQLite ====="
    
    # Tentar criar o banco de dados SQLite e executar migrações
    echo "===== Creating SQLite database and running migrations ====="
    if [ -n "$PYTHON_CMD" ]; then
        # Criar o banco de dados e preparar o ambiente
        echo "Criando banco de dados SQLite com $PYTHON_CMD"
        $PYTHON_CMD create_empty_db.py
        
        # Tentativa de executar migrações
        echo "Executando migrações do Django para SQLite..."
        cd src || echo "Não foi possível mudar para o diretório src"
        
        cat > run_migrations.py << 'EOF'
#!/usr/bin/env python

import os
import sys
import django

# Configurar o ambiente do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contra.settings')
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
django.setup()

# Executar migrações
from django.core.management import execute_from_command_line

print("Executando migrações do Django para SQLite...")
execute_from_command_line(['manage.py', 'migrate'])
print("Migrações SQLite concluídas.")
EOF
        
        # Executar o script de migrações
        $PYTHON_CMD run_migrations.py || echo "Falha ao executar migrações para SQLite"
        cd ..
    else
        echo "Não foi possível criar o banco de dados SQLite: Python não encontrado"
        # Cria um diretório para o banco de dados caso não exista
        mkdir -p src
        # Cria um arquivo vazio para simular o banco de dados
        touch src/db.sqlite3
    fi
fi

echo "Static files structure created successfully:"
find staticfiles_build -type f | sort

echo "===== Static files build complete! =====" 