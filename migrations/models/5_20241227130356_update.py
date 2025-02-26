from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` RENAME COLUMN `salt` TO `_salt`;
        ALTER TABLE `user` RENAME COLUMN `password` TO `_password`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` RENAME COLUMN `_salt` TO `salt`;
        ALTER TABLE `user` RENAME COLUMN `_password` TO `password`;"""
