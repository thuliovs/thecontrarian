#!/bin/bash

# Script para compilar os arquivos estáticos para o deploy no Vercel
echo "===== Starting static files build process ====="
echo "Current directory: $(pwd)"
echo "Directory listing:"
ls -la
echo "===== Environment information ====="
echo "Node version: $(node --version 2>&1 || echo 'Node not found')"
echo "===== Creating static directories ====="

# Cria pasta para arquivos estáticos - vamos pular a parte de collectstatic
echo "Criando estrutura de arquivos estáticos manualmente (sem depender do collectstatic)"
mkdir -p staticfiles_build/static
mkdir -p staticfiles_build/css
mkdir -p staticfiles_build/js
mkdir -p staticfiles_build/img

# Criando arquivos CSS básicos
echo "/* Base CSS file for The Contrarian Report */" > staticfiles_build/css/style.css
echo "body{font-family:sans-serif;line-height:1.6;margin:0;padding:0;background:#f8f9fa}.navbar{background:#343a40;padding:1rem}.navbar-brand,.nav-link{color:#fff!important}.general-container{background:#fff;padding:2rem;border-radius:5px;box-shadow:0 2px 10px rgba(0,0,0,0.1);max-width:1140px;margin:2rem auto}.btn-success{background:#28a745;border-color:#28a745}.text-center{text-align:center}footer{text-align:center;padding:2rem 0;color:#6c757d}" >> staticfiles_build/css/style.css

# Criando arquivo JS básico
echo "// Base JavaScript file for The Contrarian Report" > staticfiles_build/js/main.js

# Criando arquivo CSS específico para o Vercel
echo "/* Vercel deployment CSS */" > staticfiles_build/static/vercel.css

echo "Static files structure created successfully:"
find staticfiles_build -type f | sort

echo "===== Static files build complete! =====" 