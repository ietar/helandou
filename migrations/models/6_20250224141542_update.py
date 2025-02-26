from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` ADD `reset_password_salt` VARCHAR(64);
        ALTER TABLE `user` ADD `reset_time` DATETIME(6);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` DROP COLUMN `reset_password_salt`;
        ALTER TABLE `user` DROP COLUMN `reset_time`;"""
