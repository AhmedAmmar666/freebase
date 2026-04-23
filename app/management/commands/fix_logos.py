import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from app.models import Tool
import requests
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = "Fix broken logo paths in the database"

    def handle(self, *args, **options):
        tools = Tool.objects.exclude(logo='')
        self.stdout.write(f"Checking {tools.count()} tools with logos...")
        
        count = 0
        for tool in tools:
            logo_name = tool.logo.name
            # Check if the logo path is "weird" (contains https: or extra slashes)
            if 'https:' in logo_name or logo_name.count('/') > 1:
                self.stdout.write(f"Fixing broken logo for {tool.name}: {logo_name}")
                
                # Attempt to re-download a clean version
                host = tool.host or ""
                if not host and tool.url:
                    from urllib.parse import urlparse
                    host = urlparse(tool.url).hostname or ""
                
                if host:
                    logo_url = f"https://www.google.com/s2/favicons?domain={host}&sz=128"
                    try:
                        resp = requests.get(logo_url, timeout=10)
                        if resp.status_code == 200:
                            # Use a clean name
                            clean_name = f"{slugify(tool.name or host)}_logo.png"
                            tool.logo.save(clean_name, ContentFile(resp.content), save=True)
                            count += 1
                        else:
                            # If failed, just clear it so the next scrape can try again
                            tool.logo = None
                            tool.save()
                    except Exception as e:
                        self.stdout.write(f"Error re-downloading logo for {tool.name}: {e}")
                        tool.logo = None
                        tool.save()
                else:
                    tool.logo = None
                    tool.save()

        self.stdout.write(f"Fixed {count} logos.")
