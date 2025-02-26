from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `collection` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `content_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_collecti_bookcont_15a03d6f` FOREIGN KEY (`content_id`) REFERENCES `bookcontent` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_collecti_user_87ebbc87` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='收藏';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `collection`;"""
