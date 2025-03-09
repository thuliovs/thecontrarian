#!/bin/bash

# Script para compilar os arquivos estáticos para o deploy no Vercel
echo "Building static files..."
python src/manage.py collectstatic --noinput

# Crie a pasta para os arquivos estáticos se ainda não existir
if [ ! -d "staticfiles_build" ]; then
    mkdir staticfiles_build
fi

# Copie os arquivos estáticos para a pasta de destino
cp -r src/staticfiles/* staticfiles_build/
echo "Static files build complete!" 