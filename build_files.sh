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

# Forçar o uso de MySQL
export USE_MYSQL=True
echo "Forçando USE_MYSQL=True para este build"

# Instalar dependências Python
if [ -n "$PYTHON_CMD" ]; then
    echo "===== Instalando dependências do Django ====="
    $PYTHON_CMD -m pip install -r requirements-vercel.txt
    
    # Verificar se o Django foi instalado
    if $PYTHON_CMD -c "import django; print(f'Django {django.__version__} instalado com sucesso')" 2>/dev/null; then
        echo "Django instalado com sucesso"
        
        # Preparar para migrações MySQL
        echo "===== Configurando banco de dados MySQL ====="
        cd src || echo "Não foi possível mudar para o diretório src"
        
        # Criar um script temporário para migrações
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

try:
    django.setup()
    print("Django configurado com sucesso!")
    
    # Executar migrações
    from django.core.management import execute_from_command_line
    print("Executando migrações do Django para MySQL...")
    execute_from_command_line(['manage.py', 'migrate'])
    print("Migrações MySQL concluídas com sucesso!")
except Exception as e:
    import traceback
    print(f"ERRO ao executar migrações: {e}")
    traceback.print_exc()
EOF
        
        # Executar o script de migrações MySQL
        echo "Tentando executar migrações MySQL..."
        $PYTHON_CMD run_mysql_migrations.py || echo "Falha ao executar migrações MySQL"
        cd ..
    else
        echo "Falha ao instalar Django. Não será possível executar migrações."
    fi
else
    echo "Python não encontrado. Não será possível instalar dependências ou executar migrações."
fi

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

# Copiar o arquivo de favicon (SVG)
if [ -f src/static/chart-increasing-emoji-clipart-original.svg ]; then
    echo "Copiando arquivos de favicon (SVG)"
    cp src/static/chart-increasing-emoji-clipart-original.svg staticfiles_build/
    cp src/static/chart-increasing-emoji-clipart-original.svg staticfiles_build/static/
    
    # Copiar também o novo arquivo SVG com bordas arredondadas se existir
    if [ -f src/static/chart-rounded-icon.svg ]; then
        cp src/static/chart-rounded-icon.svg staticfiles_build/
        cp src/static/chart-rounded-icon.svg staticfiles_build/static/
        echo "Arquivos de favicon copiados com sucesso (original e arredondado)"
    else
        echo "Arquivo de favicon original copiado com sucesso (arredondado não encontrado)"
    fi
else
    echo "Arquivo de favicon não encontrado"
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

# Verificar o status de SQLite vs MySQL
if [ "$USE_MYSQL" = "True" ]; then
    echo "Configurado para usar MySQL. O banco de dados deverá ser criado durante o runtime."
else
    echo "Configurado para usar SQLite como fallback."
    # Tentar criar o banco de dados vazio
    if [ -n "$PYTHON_CMD" ]; then
        $PYTHON_CMD create_empty_db.py
    else
        # Cria um diretório para o banco de dados caso não exista
        mkdir -p src
        # Cria um arquivo vazio para simular o banco de dados
        touch src/db.sqlite3
    fi
fi

echo "Static files structure created successfully:"
find staticfiles_build -type f | sort

echo "===== Static files build complete! =====" 