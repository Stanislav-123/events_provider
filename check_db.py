import asyncio

from sqlalchemy import text

from app.db.session import engine


async def check_database() -> None:
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        value = result.scalar_one()

        print(f"Database connection successful: {value}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_database())
