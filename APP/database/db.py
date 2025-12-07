# database/db.py — ПОЛНЫЙ, ИСПРАВЛЕННЫЙ, ГОТОВЫЙ К РАБОТЕ
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor

DB_CONFIG = {
    'dbname': 'tg-bot',
    'user': 'admin',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}

def create_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except OperationalError as e:
        print(f"Ошибка подключения к БД: {e}")
        return None


# Автоматическое создание колонки title
def ensure_audio_title_column():
    conn = create_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'person_audio' AND column_name = 'title'
        """)
        if not cur.fetchone():
            print("Колонка 'title' не найдена — создаём...")
            cur.execute("ALTER TABLE person_audio ADD COLUMN title TEXT DEFAULT 'Аудио'")
            conn.commit()
            print("Колонка 'title' успешно добавлена")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при создании колонки title: {e}")
        if conn:
            conn.close()

ensure_audio_title_column()


# === Пользователи ===
def save_user_to_db(user_id, username, first_name, last_name=None):
    conn = create_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name
        ''', (user_id, username, first_name, last_name))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка save_user_to_db: {e}")
        return False
    finally:
        conn.close()


def save_message_to_db(user_id, message_text):
    conn = create_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO messages (user_id, message_text) VALUES (%s, %s)', (user_id, message_text))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка save_message_to_db: {e}")
        return False
    finally:
        conn.close()


# === Люди ===
def add_person_to_db(name: str, description: str):
    conn = create_connection()
    if not conn: return None
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO people (name, description) VALUES (%s, %s) RETURNING id', (name, description))
        pid = cur.fetchone()[0]
        conn.commit()
        return pid
    except Exception as e:
        print(f"Ошибка add_person_to_db: {e}")
        return None
    finally:
        conn.close()


def get_person_by_id(person_id: int):
    conn = create_connection()
    if not conn: return None
    try:
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute('SELECT id, name, description, photo1_file_id, created_at FROM people WHERE id = %s', (person_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Ошибка get_person_by_id: {e}")
        return None
    finally:
        conn.close()


def get_all_people():
    conn = create_connection()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute('SELECT id, name, description, photo1_file_id, created_at FROM people ORDER BY id')
        return cur.fetchall()
    except Exception as e:
        print(f"Ошибка get_all_people: {e}")
        return []
    finally:
        conn.close()


def delete_person(person_id: int):
    conn = create_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM people WHERE id = %s', (person_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка delete_person: {e}")
        return False
    finally:
        conn.close()


def update_person_photo(person_id: int, file_id: str):
    conn = create_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute('UPDATE people SET photo1_file_id = %s WHERE id = %s', (file_id, person_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка update_person_photo: {e}")
        return False
    finally:
        conn.close()


# === АУДИО (много на человека) ===
def add_person_audio(person_id: int, audio_file_id: str, title: str = "Аудио") -> int:
    conn = create_connection()
    if not conn: return None
    try:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO person_audio (person_id, audio_file_id, title)
            VALUES (%s, %s, %s) RETURNING id
        ''', (person_id, audio_file_id, title))
        audio_id = cur.fetchone()[0]
        conn.commit()
        return audio_id
    except Exception as e:
        print(f"Ошибка add_person_audio: {e}")
        return None
    finally:
        conn.close()


def get_person_audios(person_id: int):
    conn = create_connection()
    if not conn: return []
    try:
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute(
            "SELECT id, audio_file_id, COALESCE(title, 'Аудио') AS title FROM person_audio WHERE person_id = %s ORDER BY id",
            (person_id,)
        )
        return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"Ошибка get_person_audios: {e}")
        return []
    finally:
        conn.close()


def get_audio_info(audio_id: int):
    conn = create_connection()
    if not conn: return None
    try:
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute(
            "SELECT person_id, audio_file_id, COALESCE(title, 'Аудио') AS title FROM person_audio WHERE id = %s",
            (audio_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Ошибка get_audio_info: {e}")
        return None
    finally:
        conn.close()


def delete_audio(audio_id: int):
    conn = create_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM person_audio WHERE id = %s', (audio_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка delete_audio: {e}")
        return False
    finally:
        conn.close()


def get_people_with_any_audio():
    conn = create_connection()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT DISTINCT p.id, p.name FROM people p
            JOIN person_audio pa ON p.id = pa.person_id
            ORDER BY p.name
        ''')
        return cur.fetchall()
    except Exception as e:
        print(f"Ошибка get_people_with_any_audio: {e}")
        return []
    finally:
        conn.close()


# === Дополнительно ===
def get_people_count():
    conn = create_connection()
    if not conn: return 0
    try:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM people')
        return cur.fetchone()[0]
    except Exception as e:
        print(f"Ошибка get_people_count: {e}")
        return 0
    finally:
        conn.close()


def search_people_by_name(name: str):
    conn = create_connection()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute('SELECT id, name, description, photo1_file_id FROM people WHERE name ILIKE %s', (f'%{name}%',))
        return cur.fetchall()
    except Exception as e:
        print(f"Ошибка search_people_by_name: {e}")
        return []
    finally:
        conn.close()