#!/bin/bash

# Script para executar durante o deploy no Vercel
echo "===== Iniciando configuração de banco de dados para o deploy ====="

# Garantir que estamos usando MySQL
export USE_MYSQL=True

# Instalar dependências
echo "Instalando dependências do Python..."
pip install -r requirements-vercel.txt

# Verificar instalação
echo "Verificando instalação do Django..."
python -c "import django; print(f'Django {django.get_version()} instalado com sucesso.')"

# Executar migrações
echo "Aplicando migrações do Django..."
cd src
python manage.py showmigrations
python manage.py migrate

echo "Migrações aplicadas com sucesso!"
cd ..

# Continuar com o build normal
echo "Executando build de assets estáticos..."
./build_files.sh

echo "===== Configuração de banco de dados concluída! =====" 