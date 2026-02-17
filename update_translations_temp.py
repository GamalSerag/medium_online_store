import os
import django
from django.core.management import call_command

# Settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

# Paths
base_dir = r'D:\Django_projects\medium_online_store'
po_file = os.path.join(base_dir, 'locale', 'ar', 'LC_MESSAGES', 'django.po')

# New translations to append
new_translations = """

#: manually added
msgid "Successful Orders"
msgstr "الطلبات الناجحة"

#: manually added
msgid "Pending"
msgstr "قيد الانتظار"

#: manually added
msgid "Confirmed"
msgstr "تم التأكيد"

#: manually added
msgid "Shipped"
msgstr "تم الشحن"

#: manually added
msgid "Delivered"
msgstr "تم التوصيل"

#: manually added
msgid "Cancelled"
msgstr "ملغي"
"""

# Check for duplicates before appending (simple check)
try:
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'msgid "Successful Orders"' not in content:
        print("Appending new translations...")
        with open(po_file, 'a', encoding='utf-8') as f:
            f.write(new_translations)
    else:
        print("Translations already present.")

except Exception as e:
    print(f"Error updating PO file: {e}")

# Compile messages
print("Compiling messages...")
try:
    call_command('compilemessages', ignore=['venv'], locale=['ar'])
    print("Compilation successful.")
except Exception as e:
    print(f"Compilation failed: {e}")
