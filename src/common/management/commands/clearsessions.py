"""
Management command to clear expired sessions from the database.
"""

import logging
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Command to clear expired sessions from the database.
    
    This command can be run manually or scheduled as a cron job to periodically
    clean up expired sessions from the database, improving performance and
    reducing database size.
    """
    help = 'Clear expired sessions from the database'

    def handle(self, *args, **options):
        """
        Execute the command to clear expired sessions.
        
        This method:
        1. Gets the current time
        2. Deletes all sessions that have expired
        3. Logs and outputs the number of sessions deleted
        """
        now = timezone.now()
        expired_sessions = Session.objects.filter(expire_date__lt=now)
        count = expired_sessions.count()
        expired_sessions.delete()
        
        logger.info(f"Deleted {count} expired sessions")
        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted {count} expired sessions")
        ) 