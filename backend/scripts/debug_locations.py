import sys
import os
import asyncio

# Add backend directory to python path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "backend")))

from app.db.session import async_session_maker
from app.repositories.user_repository import UserRepository
from app.repositories.business_repository import BusinessRepository
from sqlalchemy import text


async def main():
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        business_repo = BusinessRepository(session)

        # 1. Get User
        user = await user_repo.get_by_email("nikita@hairsalon.se")
        if not user:
            print("❌ User not found")
            return

        print(f"✅ User found: {user.first_name} (ID: {user.id})")

        # 2. Get Business via Repository (Simulating API call)
        businesses = await business_repo.get_businesses(owner_id=user.id)
        if not businesses:
            print("❌ No business found for this owner")

            # DEBUG: Check if ANY business exists
            result = await session.execute(text("SELECT * FROM businesses LIMIT 1"))
            row = result.fetchone()
            if row:
                print(
                    f"   Note: A business exists in DB with owner_id={row.owner_id}. Does it match user.id?"
                )
            return

        business = businesses[0]
        print(f"✅ Business found: {business.name} (ID: {business.id})")

        # 3. Get Locations
        # Simulate business detail fetch
        result = await session.execute(
            text("SELECT * FROM locations WHERE business_id = :bid"),
            {"bid": business.id},
        )
        locations = result.fetchall()

        print(f"📍 Locations found: {len(locations)}")
        for loc in locations:
            print(f"   - {loc.name} (ID: {loc.id})")


if __name__ == "__main__":
    asyncio.run(main())
