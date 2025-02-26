from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `comment` DROP FOREIGN KEY `fk_comment_user_3a6dae6d`;
        ALTER TABLE `comment` RENAME COLUMN `user_id` TO `author_id`;
        ALTER TABLE `comment` ADD CONSTRAINT `fk_comment_user_ad794575` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `comment` DROP FOREIGN KEY `fk_comment_user_ad794575`;
        ALTER TABLE `comment` RENAME COLUMN `author_id` TO `user_id`;
        ALTER TABLE `comment` ADD CONSTRAINT `fk_comment_user_3a6dae6d` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;"""
