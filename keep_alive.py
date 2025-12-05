"""
Keep-alive service to prevent Render from sleeping due to inactivity.

This module pings the server at random intervals (4-6 minutes) to keep it active.

Author: AI Assistant
Created: 2025-12-05
"""

import os
import logging
import random
import requests
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)


class KeepAliveService:
    """Service to keep the Render app awake by pinging it periodically."""
    
    def __init__(self, app_url):
        """
        Initialize the keep-alive service.
        
        Args:
            app_url: The URL of the application to ping
        """
        self.app_url = app_url.rstrip('/')
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def ping_server(self):
        """Ping the server to keep it awake."""
        try:
            response = requests.get(f'{self.app_url}/', timeout=10)
            if response.status_code == 200:
                logger.info(f'✅ Keep-alive ping successful')
            else:
                logger.warning(f'⚠️ Keep-alive ping returned status {response.status_code}')
        except Exception as e:
            logger.error(f'❌ Keep-alive ping failed: {str(e)}')
    
    def schedule_next_ping(self):
        """Schedule the next ping at a random interval between 4-6 minutes."""
        # Random interval between 240-360 seconds (4-6 minutes)
        interval = random.randint(240, 360)
        logger.info(f'⏰ Next keep-alive ping scheduled in {interval} seconds ({interval/60:.1f} minutes)')
        
        # Remove existing job if any
        if self.scheduler.get_job('keep_alive_ping'):
            self.scheduler.remove_job('keep_alive_ping')
        
        # Schedule the ping using interval trigger
        from datetime import datetime, timedelta
        run_time = datetime.now() + timedelta(seconds=interval)
        
        self.scheduler.add_job(
            self.ping_and_reschedule,
            'date',
            run_date=run_time,
            id='keep_alive_ping',
            replace_existing=True
        )
    
    def ping_and_reschedule(self):
        """Ping the server and schedule the next ping."""
        self.ping_server()
        self.schedule_next_ping()
    
    def start(self):
        """Start the keep-alive service."""
        if not self.is_running:
            logger.info(f'🚀 Starting keep-alive service for {self.app_url}')
            self.scheduler.start()
            self.schedule_next_ping()
            self.is_running = True
            logger.info('✅ Keep-alive service started')
    
    def stop(self):
        """Stop the keep-alive service."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info('🛑 Keep-alive service stopped')
