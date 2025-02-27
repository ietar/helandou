from enum import Enum, IntEnum
from tortoise import fields
# from tortoise.models import Model
# from pydantic import EmailStr
from utils.models import ModelA, LogicalDeleteMixin


class Book(ModelA, LogicalDeleteMixin):
    """
    书籍
    """
    book_name = fields.CharField(max_length=64, index=True)
    author = fields.ForeignKeyField(model_name="models.User", related_name="books")  # 作者
    digest = fields.TextField()  # 简介
    # current = fields.IntField()
    read_count = fields.IntField(default=0, description="阅读次数")
    collect_count = fields.IntField(default=0, description="收藏数")
    using = fields.BooleanField(default=False, description="是否写入中")


class BookContent(ModelA, LogicalDeleteMixin):
    """
    书籍正文
    """
    book = fields.ForeignKeyField(model_name="models.Book", related_name="contents")  # 所属书籍
    chapter_order = fields.IntField(description="章节数", index=True, unique=True)
    chapter = fields.CharField(max_length=64, description="章节名")
    content = fields.TextField(description="正文内容")
    collect_count = fields.IntField(default=0, description="收藏数")
    read_count = fields.IntField(default=0, description="阅读数")

    class Meta:
        ordering = ["chapter_order"]


class Comment(ModelA):
    """
    评论
    """
    author = fields.ForeignKeyField(
        model_name="models.User",
        related_name="comments",
        description="评论用户"
    )
    book_content = fields.ForeignKeyField(
        model_name="models.BookContent",
        related_name="comments",
        description="关联章节",
    )
    parent_comment = fields.ForeignKeyField(
        model_name="models.Comment",
        related_name="replies",
        null=True,
        description="父级评论"
    )
    content = fields.TextField(description="评论内容")
    agree_count = fields.IntField(default=0, description="点赞数")

    class Meta:
        table = "comment"
        indexes = [("book_content", "create_time")]


class CommentAgree(ModelA):
    """
    点赞
    """
    user = fields.ForeignKeyField(model_name="models.User", related_name="agrees")
    comment = fields.ForeignKeyField(model_name="models.Comment", related_name="agrees")


class Collection(ModelA):
    """
    收藏
    """
    user = fields.ForeignKeyField(model_name="models.User", related_name="collections")
    content = fields.ForeignKeyField(model_name="models.BookContent")


class LevelEnum(IntEnum):
    unvalidated = 1
    normal = 2
    admin = 5
    root = 10


class User(ModelA, LogicalDeleteMixin):
    username = fields.CharField(max_length=32, description="用户名", db_index=True, unique=True)
    _password = fields.CharField(max_length=128, description="密码")
    email = fields.CharField(max_length=128, description="邮箱")
    level = fields.IntEnumField(enum_type=LevelEnum, description="权限等级")
    mobile = fields.CharField(max_length=16, description="手机", default="0", db_index=True, unique=True)
    last_login = fields.DatetimeField(null=True, description="上次登录时间")
    login_ip = fields.IntField(null=True, description="登录ip")
    _salt = fields.CharField(max_length=128, description="避免同样密码加密得同样")
    _reset_password_salt = fields.CharField(max_length=64, null=True, blank=True, description="重置密码salt")
    reset_time = fields.DatetimeField(null=True, description="重置密码时间")

    def get_salt(self):
        return self._salt

    def get_pwd(self):
        return self._password


class CellEnum(Enum):
    """格子类型"""
    void = 0
    grass = 1
    sea = 2


class CellState(Enum):
    """格子状态"""
    normal = 0
    burn = 1
    blocked = 2


class Cell(object):
    _type: CellEnum  # 类型
    state: CellState  # 状态

    def __init__(self, _type: str):
        self._type = CellEnum[_type]
        self.state = CellState["normal"]

    def __str__(self):
        # return f"Cell type:{self._type.name} state:{self.state}"
        return str(self.to_dict())

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            'type': self._type.name,
            'state': self.state.name
        }


class Area(ModelA, LogicalDeleteMixin):
    """区域"""
    # id = fields.IntField(pk=True, generated=True)
    name = fields.CharField(max_length=32, default="", description="区域名", db_index=True)
    father = fields.ForeignKeyField(model_name="models.Area", null=True, related_name="children")
    # deleted = fields.BooleanField(default=False, description="逻辑删除", db_index=True)


class PokeMap(ModelA, LogicalDeleteMixin):
    """地图"""
    # id = fields.IntField(pk=True, generated=True)
    name = fields.CharField(max_length=32, default="", description="地图名", db_index=True)
    width = fields.IntField()
    height = fields.IntField()
    _cells = fields.JSONField()
    # deleted = fields.BooleanField(default=False, description="逻辑删除", db_index=True)
    author = fields.CharField(null=True, max_length=32)
    cells: list[list[Cell]]  # 格子

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.cells = [[Cell("void")] * self.width for _ in range(self.height)]
        self.make_void_cells()
        # self.save_cell()

    def make_void_cells(self):
        """初始化为空格子"""
        self.cells = [[CellEnum.void] * self.width for _ in range(self.height)]
        # self._cells = json.dumps(self.cells, default=self.cell_serializer_ez)
        self._cells = self.cells

    def get_cells(self):
        # print(f"type: {type(self._cells)}, {self._cells}")
        return self._cells
        # return json.loads(self._cells)

    @property
    def scale(self):
        """地图的总格子数"""
        return self.width * self.height

    # @staticmethod
    # def cell_serializer(o):
    #     if isinstance(o, Cell):
    #         return o.to_dict()
    #     else:
    #         return json.dumps(o)

    # @staticmethod
    # def cell_serializer_ez(o):
    #     return o.value
    #
    # def save_cell(self):
    #     # print(f"{self._cells = }")
    #     # print(f"{self.cells = }")
    #     # self._cells = json.dumps(self.cells, default=self.cell_serializer)
    #     self._cells = json.dumps(self.cells, default=self.cell_serializer_ez)
    #
    # def set_cell(self, value: str, x: int, y: int):
    #     self.cells[x][y] = Cell(value)

    # async def save(self, *args, **kwargs) -> None:
    #     # self.save_cell()
    #     await super().save(*args, **kwargs)


if __name__ == '__main__':
    # register_tortoise(app=app, config=setting1)
    # import uvicorn
    # uvicorn.run(app="orm1:app", port=8080, reload=True)
    pass
