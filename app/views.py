from django.shortcuts import render
from .models import Category, Tool
from collections import defaultdict

def index(request):
    all_tools = Tool.objects.select_related('category').all()
    
    # Group tools by host
    # If host is empty, we treat each tool as its own "host" (unique key)
    grouped_data = defaultdict(list)
    for tool in all_tools:
        key = tool.host if tool.host else f"unique_{tool.id}"
        grouped_data[key].append(tool)
    
    tools_grouped = []
    for host, tools in grouped_data.items():
        first_tool = tools[0]
        
        # Collect all categories for this host group for filtering
        categories = list(set(t.category.name for t in tools))
        
        # For the UI, we'll pick the first tool's accent and featured status if any are featured
        featured = any(t.featured for t in tools)
        accent = first_tool.accent
        
        # If there's only one tool, we'll use its name, otherwise use the host name
        display_name = first_tool.name if len(tools) == 1 else host.capitalize()
        
        tools_grouped.append({
            'host': host,
            'name': display_name,
            'logo': first_tool.logo,
            'accent': accent,
            'featured': featured,
            'category': ", ".join(categories), # For display
            'filter_categories': categories,     # For JS filtering
            'tools': tools,
            'is_grouped': len(tools) > 1,
            'glyph': first_tool.glyph or display_name[0]
        })

    # Sort to keep some consistency
    tools_grouped.sort(key=lambda x: x['name'])

    # For the sidebar: group tools by category
    categories_with_tools = []
    for cat in Category.objects.prefetch_related('tools').all():
        cat_tools = cat.tools.all()
        if cat_tools.exists():
            cat.tools_list = cat_tools
            categories_with_tools.append(cat)

    return render(request, "index.html", {
        "tools": tools_grouped,
        "categories": Category.objects.all(),
        "sidebar_categories": categories_with_tools,
    })
