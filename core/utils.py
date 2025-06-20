# core/utils.py
import uuid
import os
from django.conf import settings

def get_chart_path():
    chart_name = f"{uuid.uuid4().hex}.png"
    chart_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'charts')
    os.makedirs(chart_dir, exist_ok=True)
    return os.path.join(chart_dir, chart_name), f"charts/{chart_name}"
