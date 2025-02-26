from typing import List
from tortoise import Model
from tortoise import fields


class ModelA(Model):
    """
    包含自增id create_time和update_time
    """
    id = fields.IntField(primary_key=True)
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class LogicalDeleteMixin(Model):
    """
    多继承用mixin
    尝试改写delete方法
    """
    deleted = fields.BooleanField(default=False, description="逻辑删除", db_index=True)

    async def delete(self, **kwargs):
        self.deleted = True
        await self.save(update_fields=["deleted"])
        # await super().delete(**kwargs)

    class Meta:
        abstract = True


def access_able(model: object) -> List[str]:
    return [member for member in model.__dict__ if not member.startswith("_")]
