from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `books` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted` BOOL NOT NULL  COMMENT '逻辑删除' DEFAULT 0,
    `book_name` VARCHAR(64) NOT NULL,
    `digest` LONGTEXT NOT NULL,
    `read_count` INT NOT NULL  COMMENT '阅读次数' DEFAULT 0,
    `collect_count` INT NOT NULL  COMMENT '收藏数' DEFAULT 0,
    `using` BOOL NOT NULL  COMMENT '是否写入中' DEFAULT 0,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_book_user_325b1912` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    KEY `idx_book_deleted_bcdb7f` (`deleted`),
    KEY `idx_book_book_na_a290f0` (`book_name`)
) CHARACTER SET utf8mb4 COMMENT='书籍';
        CREATE TABLE IF NOT EXISTS `bookcontent` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted` BOOL NOT NULL  COMMENT '逻辑删除' DEFAULT 0,
    `chapter_order` INT NOT NULL  COMMENT '章节数',
    `chapter` VARCHAR(64) NOT NULL  COMMENT '章节名',
    `content` LONGTEXT NOT NULL  COMMENT '正文内容',
    `collect_count` INT NOT NULL  COMMENT '收藏数' DEFAULT 0,
    `read_count` INT NOT NULL  COMMENT '阅读数' DEFAULT 0,
    `book_id` INT NOT NULL,
    CONSTRAINT `fk_bookcont_book_9d98ec05` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`) ON DELETE CASCADE,
    KEY `idx_bookcontent_deleted_36a777` (`deleted`)
) CHARACTER SET utf8mb4 COMMENT='书籍正文';
        CREATE TABLE IF NOT EXISTS `comment` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `content` LONGTEXT NOT NULL  COMMENT '评论内容',
    `agree_count` INT NOT NULL  COMMENT '点赞数' DEFAULT 0,
    `book_content_id` INT NOT NULL COMMENT '关联章节',
    `parent_comment_id` INT COMMENT '父级评论',
    `user_id` INT NOT NULL COMMENT '评论用户',
    CONSTRAINT `fk_comment_bookcont_ce51b3ae` FOREIGN KEY (`book_content_id`) REFERENCES `bookcontent` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_comment_comment_0ad00a22` FOREIGN KEY (`parent_comment_id`) REFERENCES `comment` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_comment_user_3a6dae6d` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    KEY `idx_comment_book_co_48ce23` (`book_content_id`, `create_time`)
) CHARACTER SET utf8mb4 COMMENT='评论';
        ALTER TABLE `user` ADD `_reset_password_salt` VARCHAR(64)   COMMENT '重置密码salt';
        ALTER TABLE `user` DROP COLUMN `reset_password_salt`;
        ALTER TABLE `user` MODIFY COLUMN `reset_time` DATETIME(6)   COMMENT '重置密码时间';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` ADD `reset_password_salt` VARCHAR(64);
        ALTER TABLE `user` DROP COLUMN `_reset_password_salt`;
        ALTER TABLE `user` MODIFY COLUMN `reset_time` DATETIME(6);
        DROP TABLE IF EXISTS `books`;
        DROP TABLE IF EXISTS `bookcontent`;
        DROP TABLE IF EXISTS `comment`;"""
