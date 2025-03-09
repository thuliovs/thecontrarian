#!/bin/bash

# Script para compilar os arquivos estáticos para o deploy no Vercel
echo "===== Starting static files build process ====="
echo "Current directory: $(pwd)"
echo "Directory listing:"
ls -la
echo "===== Environment information ====="
echo "Python version: $(python --version 2>&1 || echo 'Python not found')"
echo "Node version: $(node --version 2>&1 || echo 'Node not found')"
echo "===== Creating static directories ====="

# Cria pasta para arquivos estáticos
mkdir -p staticfiles_build/static
echo "Created staticfiles_build/static"

# Tenta usar o Python específico do Vercel
if command -v python3.9 &> /dev/null
then
    echo "Using Python 3.9"
    python3.9 src/manage.py collectstatic --noinput || echo "Failed collecting statics with python3.9"
elif command -v python3 &> /dev/null
then
    echo "Using Python 3"
    python3 src/manage.py collectstatic --noinput || echo "Failed collecting statics with python3"
elif command -v python &> /dev/null
then
    echo "Using default Python"
    python src/manage.py collectstatic --noinput || echo "Failed collecting statics with python"
else
    echo "Python not found, creating placeholder files"
    # Criar um arquivo CSS simples como placeholder
    mkdir -p src/staticfiles/css
    echo "/* Placeholder CSS file */" > src/staticfiles/css/placeholder.css
    
    # Criar um arquivo JS simples como placeholder
    mkdir -p src/staticfiles/js
    echo "// Placeholder JavaScript file" > src/staticfiles/js/placeholder.js
fi

echo "===== Checking static files ====="
# Garante que há algum conteúdo na pasta de destino
if [ ! -d "src/staticfiles" ]; then
    echo "Creating src/staticfiles directory"
    mkdir -p src/staticfiles/css
    echo "/* Placeholder CSS file */" > src/staticfiles/css/placeholder.css
fi

# Garantir que sempre haja pelo menos um arquivo na pasta de destino
echo "/* Vercel deployment CSS */" > staticfiles_build/static/vercel.css
echo "Created vercel.css in staticfiles_build/static"

# Tenta copiar arquivos estáticos
echo "Trying to copy static files"
if [ -d "src/staticfiles" ] && [ "$(ls -A src/staticfiles 2>/dev/null)" ]; then
    echo "Copying files from src/staticfiles to staticfiles_build"
    cp -rv src/staticfiles/* staticfiles_build/ || echo "Error copying static files"
else
    echo "src/staticfiles is empty or doesn't exist, creating placeholder"
    mkdir -p staticfiles_build/css
    echo "/* Placeholder CSS file */" > staticfiles_build/css/style.css
fi

echo "Final directory structure in staticfiles_build:"
find staticfiles_build -type f | sort

echo "===== Static files build complete! =====" 