import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from app.bot import create_bot, create_dispatcher
from app.database.connection import DatabaseConnection
from app.database.migrations import run_migrations
from app.utils.logger import setup_logging

@asynccontextmanager
async def lifespan():
    # Startup
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        DatabaseConnection.init_pool()
        await run_migrations()
        logger.info("Application started")
        yield
    finally:
        # Shutdown
        DatabaseConnection.close_all()
        logger.info("Application stopped")

async def main():
    async with lifespan():
        bot = await create_bot()
        dp = await create_dispatcher()
        
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)