from sqlalchemy import select
from db.models import Server
from db.session import AsyncSessionLocal


class ServerService:
    async def get_or_create_server(self, guild):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Server).where(Server.id == guild.id)
            )
            server = result.scalar_one_or_none()

            if server is None:
                server = Server(id=guild.id, name=guild.name)
                session.add(server)
                await session.commit()
                await session.refresh(server)

            return server

    async def close(self):
        pass