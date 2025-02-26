from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `area` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted` BOOL NOT NULL  COMMENT '逻辑删除' DEFAULT 0,
    `name` VARCHAR(32) NOT NULL  COMMENT '区域名' DEFAULT '',
    `father_id` INT,
    CONSTRAINT `fk_area_area_d1c451db` FOREIGN KEY (`father_id`) REFERENCES `area` (`id`) ON DELETE CASCADE,
    KEY `idx_area_deleted_bb5c99` (`deleted`),
    KEY `idx_area_name_ed84d5` (`name`)
) CHARACTER SET utf8mb4 COMMENT='区域';
CREATE TABLE IF NOT EXISTS `pokemap` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted` BOOL NOT NULL  COMMENT '逻辑删除' DEFAULT 0,
    `name` VARCHAR(32) NOT NULL  COMMENT '地图名' DEFAULT '',
    `width` INT NOT NULL,
    `height` INT NOT NULL,
    `_cells` JSON NOT NULL,
    `author` VARCHAR(32),
    KEY `idx_pokemap_deleted_6efcc5` (`deleted`),
    KEY `idx_pokemap_name_b8ae4f` (`name`)
) CHARACTER SET utf8mb4 COMMENT='地图';
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `create_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted` BOOL NOT NULL  COMMENT '逻辑删除' DEFAULT 0,
    `username` VARCHAR(32) NOT NULL  COMMENT '用户名',
    `password` VARCHAR(128) NOT NULL  COMMENT '密码',
    `email` VARCHAR(128) NOT NULL  COMMENT '邮箱',
    `level` SMALLINT NOT NULL  COMMENT '权限等级',
    `mobile` VARCHAR(16) NOT NULL  COMMENT '手机' DEFAULT '0',
    `last_login` DATETIME(6)   COMMENT '上次登录时间',
    `login_ip` INT   COMMENT '登录ip',
    KEY `idx_user_deleted_097fcb` (`deleted`),
    KEY `idx_user_usernam_9987ab` (`username`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
