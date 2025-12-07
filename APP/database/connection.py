import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import Generator, Any
from app.config import config
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _pool = None
    
    @classmethod
    def init_pool(cls, min_conn=1, max_conn=10):
        if cls._pool is None:
            try:
                cls._pool = SimpleConnectionPool(
                    min_conn, max_conn,
                    **config.db.__dict__
                )
                logger.info("Database connection pool initialized")
            except Exception as e:
                logger.error(f"Failed to initialize connection pool: {e}")
                raise
    
    @classmethod
    @contextmanager
    def get_connection(self, cursor_factory=DictCursor) -> Generator[Any, None, None]:
        conn = None
        try:
            conn = self._pool.getconn()
            conn.autocommit = False
            cursor = conn.cursor(cursor_factory=cursor_factory)
            yield cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)
    
    @classmethod
    def close_all(self):
        if self._pool:
            self._pool.closeall()
            logger.info("Database connections closed")