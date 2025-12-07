print("Тест импортов...")

try:
    from aiogram import Bot
    print("✅ aiogram импортирован")
except ImportError as e:
    print(f"❌ Ошибка aiogram: {e}")

try:
    from config import TOKEN
    print(f"✅ config импортирован, TOKEN: {TOKEN[:10]}...")
except ImportError as e:
    print(f"❌ Ошибка config: {e}")

try:
    from database.db import create_connection
    print("✅ database импортирован")
except ImportError as e:
    print(f"❌ Ошибка database: {e}")

try:
    from keyboards.main import main_keyboard
    print("✅ keyboards импортирован")
except ImportError as e:
    print(f"❌ Ошибка keyboards: {e}")

try:
    from admin_panel import admin_router
    print("✅ admin_panel импортирован")
except ImportError as e:
    print(f"❌ Ошибка admin_panel: {e}")

print("\nВсе импорты проверены")
