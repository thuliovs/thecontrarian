"""
Aplicação WSGI simples para o Vercel que serve uma página estática.
"""

import os
import sys

def app(environ, start_response):
    """
    Aplicação WSGI simples que serve a página inicial do The Contrarian Report
    """
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    
    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>The Contrarian Report</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            header {
                background-color: #343a40;
                color: #fff;
                padding: 20px;
                text-align: center;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            h1 {
                margin: 0;
                font-size: 2.5rem;
            }
            .tagline {
                font-style: italic;
                margin-top: 10px;
            }
            .container {
                background-color: #fff;
                padding: 30px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .btn {
                display: inline-block;
                background-color: #28a745;
                color: #fff;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            .btn:hover {
                background-color: #218838;
            }
            .text-center {
                text-align: center;
            }
            .mb-4 {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>The Contrarian Report</h1>
            <p class="tagline">Perspectivas únicas sobre mercados financeiros</p>
        </header>
        
        <div class="container">
            <div class="text-center">
                <h2>Em Manutenção</h2>
                <h5>Perspectivas únicas e rentáveis sobre os mercados de capitais!</h5>
                <p class="mb-4">Estamos fazendo algumas atualizações para melhorar sua experiência. Por favor, volte em breve para acessar nossa coleção exclusiva de relatórios e artigos.</p>
                <p><strong>Data prevista para retorno: Em breve</strong></p>
                
                <a class="btn" href="mailto:contato@thecontrarian.com">
                    <i class="fa fa-envelope" aria-hidden="true"></i> 
                    Entre em Contato
                </a>
            </div>
        </div>
        
        <footer class="text-center" style="margin-top: 40px; padding: 20px; color: #6c757d;">
            <p>&copy; 2024 The Contrarian Report. Todos os direitos reservados.</p>
        </footer>
    </body>
    </html>
    """
    
    return [html.encode('utf-8')] 