import re
from urllib.parse import urlparse

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

import requests
from app.models import Category, Tool


def download_image(url):
    try:
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        resp.raise_for_status()
        return ContentFile(resp.content)
    except Exception:
        return None


class Command(BaseCommand):
    help = "Scrape https://free-for.dev README.md and save tools"

    def add_arguments(self, parser):
        parser.add_argument(
            "--url", 
            help="URL to the README.md file", 
            default="https://free-for.dev/README.md"
        )

    def handle(self, *args, **options):
        readme_url = options["url"]
        self.stdout.write(f"Fetching {readme_url} ...")

        try:
            response = requests.get(readme_url, timeout=10)
            response.raise_for_status()
            content = response.text
        except Exception as e:
            self.stderr.write(f"Failed to fetch {readme_url}: {e}")
            return

        # Split content by sections (headings)
        # We look for ## or ### headings
        sections = re.split(r'\n(?=#{2,3}\s)', content)
        
        self.stdout.write(f"Found {len(sections)} sections")

        for section in sections:
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            header_line = lines[0]
            category_match = re.match(r'#{2,3}\s+(.*)', header_line)
            if not category_match:
                continue
                
            category_name = category_match.group(1).strip()
            
            # Skip some common non-category headers
            if category_name.lower() in ['table of contents', 'contributing', 'license']:
                continue

            cat_obj, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'slug': slugify(category_name)}
            )
            self.stdout.write(f"Processing category: {category_name}")

            count = 0
            # Extract tools: * [Name](URL) - Description
            # Some descriptions might be multi-line or have extra text, but usually it's one line
            for line in lines[1:]:
                tool_match = re.match(r'^\s*\*\s*\[(.*?)\]\((.*?)\)\s*-\s*(.*)$', line)
                if tool_match:
                    name = tool_match.group(1).strip()
                    url = tool_match.group(2).strip()
                    desc = tool_match.group(3).strip()
                    
                    parsed_url = urlparse(url)
                    host = parsed_url.hostname or ""

                    # Create or update tool
                    import random
                    accents = ['lime', 'coral', 'violet', 'sky']
                    
                    tool_obj, created = Tool.objects.update_or_create(
                        url=url,
                        defaults={
                            'category': cat_obj,
                            'name': name,
                            'description': desc,
                            'host': host,
                            'accent': random.choice(accents),
                            'featured': random.random() < 0.1, # 10% chance to be featured
                        }
                    )
                    
                    # Fetch logo if not already present
                    if not tool_obj.logo:
                        # Try icon.horse first as it is better for subdomains
                        logo_url = f"https://icon.horse/icon/{host}"
                        img_content = download_image(logo_url)
                        
                        if not img_content:
                            # Fallback to Google Favicon service
                            logo_url = f"https://www.google.com/s2/favicons?domain={host}&sz=128"
                            img_content = download_image(logo_url)

                        if img_content:
                            tool_obj.logo.save(
                                f"{slugify(name)}_logo.png", 
                                img_content, 
                                save=True
                            )
                    
                    count += 1
                
            self.stdout.write(f"  Imported {count} tools")

        self.stdout.write("Scrape complete")
