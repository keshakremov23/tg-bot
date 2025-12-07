from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from app.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

@dataclass
class User:
    id: int
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    created_at: datetime

@dataclass
class Person:
    id: int
    name: str
    description: str
    photo_file_id: Optional[str]
    created_at: datetime

@dataclass
class Audio:
    id: int
    person_id: int
    audio_file_id: str
    title: str
    created_at: datetime

class UserRepository:
    @staticmethod
    def save(user_id: int, username: Optional[str], first_name: str, last_name: Optional[str] = None) -> bool:
        try:
            with DatabaseConnection.get_connection() as cursor:
                cursor.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                ''', (user_id, username, first_name, last_name))
                return True
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            return False
    
    @staticmethod
    def save_message(user_id: int, message_text: str) -> bool:
        try:
            with DatabaseConnection.get_connection() as cursor:
                cursor.execute(
                    'INSERT INTO messages (user_id, message_text) VALUES (%s, %s)',
                    (user_id, message_text)
                )
                return True
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return False

class PersonRepository:
    @staticmethod
    def create(name: str, description: str) -> Optional[int]:
        try:
            with DatabaseConnection.get_connection() as cursor:
                cursor.execute(
                    'INSERT INTO people (name, description) VALUES (%s, %s) RETURNING id',
                    (name, description)
                )
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error creating person: {e}")
            return None
    
    @staticmethod
    def get_by_id(person_id: int) -> Optional[Person]:
        try:
            with DatabaseConnection.get_connection(RealDictCursor) as cursor:
                cursor.execute(
                    'SELECT * FROM people WHERE id = %s',
                    (person_id,)
                )
                row = cursor.fetchone()
                if row:
                    return Person(**row)
        except Exception as e:
            logger.error(f"Error getting person: {e}")
        return None
    
    @staticmethod
    def get_all() -> List[Person]:
        try:
            with DatabaseConnection.get_connection(RealDictCursor) as cursor:
                cursor.execute('SELECT * FROM people ORDER BY id')
                return [Person(**row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all people: {e}")
            return []
    
    @staticmethod
    def delete(person_id: int) -> bool:
        try:
            with DatabaseConnection.get_connection() as cursor:
                cursor.execute('DELETE FROM people WHERE id = %s', (person_id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting person: {e}")
            return False
    
    @staticmethod
    def update_photo(person_id: int, file_id: str) -> bool:
        try:
            with DatabaseConnection.get_connection() as cursor:
                cursor.execute(
                    'UPDATE people SET photo_file_id = %s WHERE id = %s',
                    (file_id, person_id)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating photo: {e}")
            return False
    
    @staticmethod
    def search_by_name(name: str) -> List[Person]:
        try:
            with DatabaseConnection.get_connection(RealDictCursor) as cursor:
                cursor.execute(
                    'SELECT * FROM people WHERE name ILIKE %s',
                    (f'%{name}%',)
                )
                return [Person(**row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error searching people: {e}")
            return []

class AudioRepository:
    @staticmethod
    def create(person_id: int, audio_file_id: str, title: str = "Аудио") -> Optional[int]:
        try:
            with DatabaseConnection.get_connection() as cursor:
                cursor.execute('''
                    INSERT INTO person_audio (person_id, audio_file_id, title)
                    VALUES (%s, %s, %s) RETURNING id
                ''', (person_id, audio_file_id, title))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error creating audio: {e}")
            return None
    
    @staticmethod
    def get_by_person_id(person_id: int) -> List[Audio]:
        try:
            with DatabaseConnection.get_connection(RealDictCursor) as cursor:
                cursor.execute(
                    'SELECT * FROM person_audio WHERE person_id = %s ORDER BY id',
                    (person_id,)
                )
                return [Audio(**row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting person audios: {e}")
            return []
    
    @staticmethod
    def get_by_id(audio_id: int) -> Optional[Audio]:
        try:
            with DatabaseConnection.get_connection(RealDictCursor) as cursor:
                cursor.execute(
                    'SELECT * FROM person_audio WHERE id = %s',
                    (audio_id,)
                )
                row = cursor.fetchone()
                if row:
                    return Audio(**row)
        except Exception as e:
            logger.error(f"Error getting audio: {e}")
        return None
    
    @staticmethod
    def delete(audio_id: int) -> bool:
        try:
            with DatabaseConnection.get_connection() as cursor:
                cursor.execute('DELETE FROM person_audio WHERE id = %s', (audio_id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting audio: {e}")
            return False
    
    @staticmethod
    def get_people_with_audio() -> List[Dict[str, Any]]:
        try:
            with DatabaseConnection.get_connection() as cursor:
                cursor.execute('''
                    SELECT DISTINCT p.id, p.name 
                    FROM people p
                    JOIN person_audio pa ON p.id = pa.person_id
                    ORDER BY p.name
                ''')
                return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting people with audio: {e}")
            return []