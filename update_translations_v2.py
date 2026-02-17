import os
import django
from django.core.management import call_command
import sys

# Settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

# Paths
base_dir = r'D:\Django_projects\medium_online_store'
po_file = os.path.join(base_dir, 'locale', 'ar', 'LC_MESSAGES', 'django.po')

# New translations to append
new_translations = """

#: manually added for order detail
msgid "Order Details"
msgstr "تفاصيل الطلب"

msgid "Back to Dashboard"
msgstr "العودة للوحة التحكم"

msgid "Order Items"
msgstr "عناصر الطلب"

msgid "Product"
msgstr "المنتج"

msgid "Price"
msgstr "السعر"

msgid "Quantity"
msgstr "الكمية"

msgid "Customer Details"
msgstr "تفاصيل العميل"

msgid "Name"
msgstr "الاسم"

msgid "Phone"
msgstr "الهاتف"

msgid "Address"
msgstr "العنوان"

msgid "Notes"
msgstr "ملاحظات"

msgid "Order Status"
msgstr "حالة الطلب"

msgid "Created"
msgstr "تم الإنشاء"

msgid "Update Status"
msgstr "تحديث الحالة"

msgid "View"
msgstr "عرض"
"""

try:
    with open(po_file, 'a', encoding='utf-8') as f:
        f.write(new_translations)
    print("Appended translations.")
except Exception as e:
    print(f"Error appending: {e}")

# Run compile_messages.py
from compile_messages import generate
print("Running compile_messages.py...")
generate()
