from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `books` DROP FOREIGN KEY `fk_book_user_325b1912`;
        ALTER TABLE `books` RENAME COLUMN `user_id` TO `author_id`;
        ALTER TABLE `books` ADD CONSTRAINT `fk_book_user_6e6cc3c3` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `books` DROP FOREIGN KEY `fk_book_user_6e6cc3c3`;
        ALTER TABLE `books` RENAME COLUMN `author_id` TO `user_id`;
        ALTER TABLE `books` ADD CONSTRAINT `fk_book_user_325b1912` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;"""
