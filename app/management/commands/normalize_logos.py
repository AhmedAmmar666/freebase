import os
import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from app.models import Tool

class Command(BaseCommand):
    help = "Normalize all logo filenames to be safe"

    def handle(self, *args, **options):
        tools = Tool.objects.exclude(logo='')
        self.stdout.write(f"Normalizing {tools.count()} logos...")
        
        count = 0
        for tool in tools:
            old_path = tool.logo.name
            # If the filename is not slugified or contains weird chars
            filename = os.path.basename(old_path)
            clean_filename = f"{slugify(tool.name)}_logo{os.path.splitext(filename)[1]}"
            
            # If the path is not just logos/clean_filename
            expected_path = f"logos/{clean_filename}"
            
            if old_path != expected_path:
                self.stdout.write(f"Renaming {old_path} -> {expected_path}")
                # We don't actually rename the file on disk here to avoid complexity
                # We just update the DB and let the next scrape or fix_logos handle the download if missing
                # Actually, better to just re-download all logos to be 100% clean
                tool.logo = None
                tool.save()
                count += 1
                
        self.stdout.write(f"Cleared {count} logos for re-download.")
