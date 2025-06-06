
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
    "CHAR_EXCEPTIONS": "ioszl10",  # 易混淆的字符 排除出验证码生成
}

custom = {
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
    "RESET_PASSWORD_EMAIL_TTL_MINUTES": 30,  # 重置密码找回邮件有效期
    "book_author_can_delete_comment": False,  # 作者是否有权删除作品下的评论
    "subscribe_content_cost_rate": 100,  # 订阅章节耗费为章节内容长度/rate 如千字章节耗费10coins
    "subscribe_min_content": 200,  # 订阅章节最小内容长度 低于该值耗费0.01
    "subscribe_min_cost": "0.01",  # 订阅章节最小内容长度 低于该值耗费subscribe_min_cost
    "decimal_places": 2,  # 十进制定点数小数位数
}

throttling_table = {
    # 不限流
    "just_let_go": [
        "^/$",
        "^/anything$",
        "^/user/logout$",
        "^/static/*",
        "^/api/user/user_exist",
        "^/get_image_code_by_uuid"
    ],
    # 限流
    "/docs": 10,
    # "/api/user/user_exist": 1,
}

