#!/usr/bin/env python
"""
Script para criar um banco de dados SQLite vazio durante o build no Vercel.
Isso garante que o arquivo existirá quando o Django tentar acessá-lo.
"""

import sqlite3
import os
from pathlib import Path

# Localização do banco de dados
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'src' / 'db.sqlite3'

print(f"Criando banco de dados SQLite vazio em: {DB_PATH}")

# Criar diretórios se necessário
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Criar banco de dados vazio
conn = sqlite3.connect(str(DB_PATH))
conn.close()

print("Banco de dados vazio criado com sucesso.") 