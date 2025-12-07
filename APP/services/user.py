from typing import Optional
from app.database.repositories import UserRepository
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    async def save_user(
        user_id: int, 
        username: Optional[str], 
        first_name: str, 
        last_name: Optional[str] = None
    ) -> bool:
        try:
            return UserRepository.save(user_id, username, first_name, last_name)
        except Exception as e:
            logger.error(f"Error in save_user service: {e}")
            return False
    
    @staticmethod
    async def save_message(user_id: int, message_text: str) -> bool:
        try:
            return UserRepository.save_message(user_id, message_text)
        except Exception as e:
            logger.error(f"Error in save_message service: {e}")
            return False
    
    @staticmethod
    async def is_admin(user_id: int) -> bool:
        from app.config import config
        return user_id in config.bot.admin_ids