
setting1 = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "127.0.0.1",
                "port": "3306",
                "user": "helandou",
                "password": "helandou_display",
                "database": "helandou",
                "minsize": 1,
                "maxsize": 5,
                "charset": "utf8mb4",
                "echo": True
            }
        }
    },
    "apps": {
        "models": {
            "models": ["models.models", "aerich.models"],
            "default_connection": "default"
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}

custom = {
    "CHAR_EXCEPTIONS": "ioszlb10",  # 易混淆的字符 排除出验证码生成
    "produce": False,  # 生产环境为True
    "image_capcha_ttl_seconds": 120,
    "redis_throttling": True,
    # "redis_throttling": False,
    "anything": {
        "search_place_holder": "吃了吗",
    },
    "CAPTCHA_EXPIRE": 300,
    "email_code_length": 6,
    "email_capcha_ttl_seconds": 600,
    "auto_captcha": "ietar",  # 万能验证码 适用于图形验证码和邮件验证码
    "RESET_PASSWORD_EMAIL_TTL_MINUTES": 10,  # 重置密码找回邮件有效期
    "book_author_can_delete_comment": False,  # 作者是否有权删除作品下的评论
    "subscribe_content_cost_rate": 100,  # 订阅章节耗费为章节内容长度/rate 如千字章节耗费10coins
    "subscribe_min_content": 100,  # 订阅章节最小内容长度 低于该值耗费subscribe_min_cost
    "subscribe_min_cost": "1",  # 订阅章节最小耗费
    "decimal_places": 0,  # 十进制定点数小数位数
    "DEFAULT_THROTTLING_SECONDS": 1,  # 默认限流间隔1秒即允许访问
    "subscribe_tax": 0.2,  # 订阅税率 为0则订阅费用完全传给作者
    "host_url": "127.0.0.1:8080",  # 主机url 暂
}

throttling_table = {
    # 不限流
    "just_let_go": [
        "^((?!/api).)*$",  # 非/api开头即页面,一律不过滤
        # "/api/comment/get_all_comments/4$",  # temp
        # "^/$",
        # "^/anything$",
        # "^/user/logout$",
        # "^/static/*",
        # "^/api/user/user_exist",
        # "^/get_image_code_by_uuid"
    ],
    # 限流 单位为秒
    "/docs$": 3,
    "/api/user/user_exist$": 0.2,
}

