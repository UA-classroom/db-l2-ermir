"""Reset database and run seed scripts."""
import argparse
import asyncio
import platform
import sys
from pathlib import Path

# Add project root to path BEFORE imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.core.database import db
from scripts.seeds.core.roles import seed_roles
from scripts.seeds.core.users import seed_users
from scripts.seeds.core.businesses import seed_businesses
from scripts.seeds.core.services import seed_services




async def reset_schema(conn):
    """Drop all tables and recreate from schema.sql."""
    schema_path = project_root / "sql" / "schema.sql"

    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return False

    print("🔄 Resetting database schema...")

    # Drop all tables (cascade to handle foreign keys)
    async with conn.cursor() as cur:
        await cur.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """)

    await conn.commit()

    # Run schema.sql
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    async with conn.cursor() as cur:
        await cur.execute(schema_sql)

    await conn.commit()
    print("✓ Schema recreated")
    return True


async def run_seeds(conn, only=None):
    """Run seed scripts in order."""

    seeds = [
        ("roles", seed_roles),
        ("users", seed_users),
        ("businesses", seed_businesses),
        ("services", seed_services),
    ]

    # Filter if --only specified
    if only:
        seeds = [(name, func) for name, func in seeds if name == only]
        if not seeds:
            print(f"❌ Unknown seed: {only}")
            return

    print(f"\n🌱 Running {len(seeds)} seed script(s)...")

    for name, seed_func in seeds:
        try:
            await seed_func(conn)
        except Exception as e:
            print(f"❌ Error seeding {name}: {e}")
            raise


async def main():
    parser = argparse.ArgumentParser(description="Reset database and run seeds")
    parser.add_argument("--only", help="Run only specific seed (e.g., 'roles', 'users')")
    parser.add_argument("--no-reset", action="store_true", help="Skip schema reset")
    args = parser.parse_args()

    print(f"🗄️  Database: {settings.DB_NAME}")

    try:
        await db.connect()

        async with db.get_connection() as conn:
            # Reset schema unless --no-reset
            if not args.no_reset:
                success = await reset_schema(conn)
                if not success:
                    return

            # Run seeds
            await run_seeds(conn, only=args.only)

        print("\n✅ Database reset complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        await db.disconnect()


if __name__ == "__main__":
    # Fix for Windows: psycopg requires SelectorEventLoop
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
