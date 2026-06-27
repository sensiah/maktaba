#!/usr/bin/env python
"""شغّل هذا الملف مرة واحدة فقط لإعداد قاعدة البيانات والبيانات الأولية"""
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
import django
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from core.models import Category, Product

print("=" * 55)
print("  متجر القرطاسية — متليلي الشعانبة")
print("  الإعداد الأولي")
print("=" * 55)

print("\n[1/4] تهيئة قاعدة البيانات...")
call_command('makemigrations', 'core', verbosity=0)
call_command('makemigrations', 'shop', verbosity=0)
call_command('migrate', verbosity=0)
print("      ✓ تمت")

print("\n[2/4] إنشاء حساب المدير...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@maktaba.dz', 'admin123')
    print("      ✓ admin / admin123")
else:
    print("      ✓ موجود مسبقاً")

print("\n[3/4] إنشاء حساب أمين الصندوق...")
if not User.objects.filter(username='cashier').exists():
    User.objects.create_user('cashier', 'cashier@maktaba.dz', 'cashier123')
    print("      ✓ cashier / cashier123")
else:
    print("      ✓ موجود مسبقاً")

print("\n[4/4] إضافة المنتجات...")
if Category.objects.count() == 0:
    c = {
        'nb': Category.objects.create(name="Notebooks",              description="دفاتر وكراسات"),
        'mk': Category.objects.create(name="Markers & Highlighters", description="ماركرات وأقلام تحديد"),
        'pc': Category.objects.create(name="Pencils & Sharpeners",   description="أقلام رصاص وبرايات"),
        'pn': Category.objects.create(name="Pens",                   description="أقلام حبر وجل"),
        'gl': Category.objects.create(name="Glue",                   description="غراء وأشرطة لاصقة"),
        'cr': Category.objects.create(name="Crayons",                description="ألوان وأقلام تلوين"),
        'fd': Category.objects.create(name="Folders",                description="ملفات ومجلدات"),
        'bd': Category.objects.create(name="Binders",                description="مجلدات حلقية"),
        'pp': Category.objects.create(name="Loose Leaf Paper",       description="أوراق مسطرة وبيضاء"),
        'ca': Category.objects.create(name="Calculators",            description="آلات حاسبة"),
        'sc': Category.objects.create(name="Scissors",               description="مقصات"),
        'kc': Category.objects.create(name="Pencil Cases",           description="محافظ أقلام"),
    }
    products = [
        ("Spiral Notebook A4",           c['nb'], "NB-001", 350,  180, 120),
        ("Hardcover Notebook A5",        c['nb'], "NB-002", 599,  300,  80),
        ("Composition Notebook",         c['nb'], "NB-003", 299,  150, 100),
        ("Highlighter Set 5 colors",     c['mk'], "MK-001", 450,  220,  90),
        ("Permanent Marker Black",       c['mk'], "MK-002", 199,   90, 150),
        ("Whiteboard Marker Set",        c['mk'], "MK-003", 599,  300,  60),
        ("HB Pencil 12 pack",            c['pc'], "PC-001", 249,  110, 200),
        ("Colored Pencils 24 colors",    c['pc'], "PC-002", 699,  350,  75),
        ("Pencil Sharpener dual hole",   c['pc'], "PC-003", 125,   50, 180),
        ("Eraser Large White",           c['pc'], "PC-004",  99,   40, 250),
        ("Ballpoint Pen Blue 10 pack",   c['pn'], "PN-001", 399,  180, 160),
        ("Gel Pen Black",                c['pn'], "PN-002", 149,   60, 200),
        ("Gel Pen Set 8 colors",         c['pn'], "PN-003", 799,  400,  55),
        ("Glue Stick 40g",               c['gl'], "GL-001", 199,   80, 140),
        ("Liquid Glue 100ml",            c['gl'], "GL-002", 249,  100, 100),
        ("Double-Sided Tape Roll",       c['gl'], "GL-003", 299,  130,  80),
        ("Wax Crayons 16 colors",        c['cr'], "CR-001", 349,  160,  90),
        ("Wax Crayons 32 colors",        c['cr'], "CR-002", 599,  280,  60),
        ("Oil Pastels 12 colors",        c['cr'], "CR-003", 499,  240,  50),
        ("A4 Document Folder Clear",     c['fd'], "FD-001", 149,   60, 200),
        ("Expanding File Folder",        c['fd'], "FD-002", 599,  280,  70),
        ("Plastic Wallet Folder A4",     c['fd'], "FD-003",  99,   40, 250),
        ("Ring Binder 2inch A4",         c['bd'], "BD-001", 499,  230,  80),
        ("Lever Arch File A4",           c['bd'], "BD-002", 649,  310,  60),
        ("Mini Binder 1inch A5",         c['bd'], "BD-003", 399,  180,  70),
        ("Lined Paper A4 100 sheets",    c['pp'], "PP-001", 249,  100, 150),
        ("Graph Paper A4 50 sheets",     c['pp'], "PP-002", 299,  130,  80),
        ("Blank Paper A4 500 sheets",    c['pp'], "PP-003", 699,  350, 100),
        ("Basic Calculator 12-digit",    c['ca'], "CA-001", 899,  450,  40),
        ("Scientific Calculator",        c['ca'], "CA-002",1999, 1000,  25),
        ("Student Scissors 7inch",       c['sc'], "SC-001", 299,  120, 120),
        ("Craft Scissors zig-zag",       c['sc'], "SC-002", 399,  180,  60),
        ("Zippered Pencil Case large",   c['kc'], "KC-001", 499,  220,  85),
        ("Clear PVC Pencil Pouch",       c['kc'], "KC-002", 249,  100, 110),
        ("Hard Shell Pencil Box",        c['kc'], "KC-003", 699,  340,  50),
    ]
    for name, cat, sku, price, cost, stock in products:
        Product.objects.create(
            name=name, category=cat, sku=sku,
            price=price, cost_price=cost, stock_quantity=stock,
            low_stock_threshold=10
        )
    print(f"      ✓ {len(products)} منتج في 12 فئة")
else:
    print("      ✓ المنتجات موجودة مسبقاً")

print("\n" + "=" * 55)
print("  اكتمل الإعداد! 🎉")
print("=" * 55)
print("\n  شغّل السيرفر:")
print("  → python manage.py runserver")
print("\n  ثم افتح المتصفح:")
print("  → المتجر:   http://127.0.0.1:8000")
print("  → الإدارة:  http://127.0.0.1:8000/dashboard/")
print("\n  الدخول:")
print("  → مدير:     admin / admin123")
print("  → صندوق:    cashier / cashier123")
print("=" * 55)
