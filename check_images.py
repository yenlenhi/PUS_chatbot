import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def main():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    result = await conn.fetch(
        "SELECT images FROM conversations WHERE images IS NOT NULL LIMIT 5"
    )
    for r in result:
        print(f"Images: {r['images']}")
    await conn.close()


asyncio.run(main())
