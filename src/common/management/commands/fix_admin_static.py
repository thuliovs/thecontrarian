"""
Management command to fix admin static files.
"""

import os
import shutil
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib import admin
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Command to fix admin static files.
    
    This command copies the Django admin static files to the static root 
    directory, ensuring they are accessible for the admin interface.
    """
    help = 'Fix admin static files'

    def handle(self, *args, **options):
        """
        Execute the command to fix admin static files.
        
        This method:
        1. Locates the Django admin static files
        2. Creates the necessary directories in the static root
        3. Copies the admin static files to the static root
        4. Logs and outputs the number of files copied
        """
        self.stdout.write(self.style.SUCCESS("Iniciando correção de arquivos estáticos de admin..."))
        
        # Tentar encontrar o caminho dos arquivos estáticos do admin
        try:
            admin_path = admin.__path__[0]
            self.stdout.write(f"Caminho do Django Admin: {admin_path}")
            
            # Verificar se o diretório de estáticos do admin existe
            admin_static_path = os.path.join(admin_path, 'static', 'admin')
            if not os.path.exists(admin_static_path):
                django_path = Path(admin_path).parent.parent  # django/contrib/admin
                admin_static_path = os.path.join(django_path, 'contrib', 'admin', 'static', 'admin')
            
            if os.path.exists(admin_static_path):
                self.stdout.write(f"Arquivos estáticos do admin encontrados em: {admin_static_path}")
                
                # Criar diretório de destino
                dest_dir = os.path.join(settings.STATIC_ROOT, 'admin')
                os.makedirs(dest_dir, exist_ok=True)
                
                # Copiar arquivos
                file_count = self._copy_directory(admin_static_path, dest_dir)
                
                self.stdout.write(
                    self.style.SUCCESS(f"Copiados {file_count} arquivos estáticos do admin")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("Não foi possível encontrar os arquivos estáticos do admin")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Erro ao corrigir arquivos estáticos do admin: {e}")
            )
    
    def _copy_directory(self, source, destination):
        """
        Recursively copy a directory to a destination.
        
        Args:
            source: Source directory path
            destination: Destination directory path
            
        Returns:
            int: Number of files copied
        """
        count = 0
        for item in os.listdir(source):
            source_item = os.path.join(source, item)
            dest_item = os.path.join(destination, item)
            
            if os.path.isdir(source_item):
                os.makedirs(dest_item, exist_ok=True)
                count += self._copy_directory(source_item, dest_item)
            else:
                shutil.copy2(source_item, dest_item)
                count += 1
        
        return count 