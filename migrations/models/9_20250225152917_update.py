from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `bookcontent` ADD INDEX `idx_bookcontent_chapter_e2bbbe` (`chapter_order`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `bookcontent` DROP INDEX `idx_bookcontent_chapter_e2bbbe`;"""
