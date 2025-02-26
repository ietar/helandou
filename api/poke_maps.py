import json
from fastapi import APIRouter
from pydantic import BaseModel
from models.models import Area, PokeMap, CellEnum

from utils.response import wrap_response

poke_maps_api = APIRouter()


@poke_maps_api.get("/areas")
async def get_all_area():
    areas = await Area.all()
    return wrap_response(areas)


@poke_maps_api.get("/maps")
async def get_all_maps():
    maps = await PokeMap.all()
    return wrap_response(maps)


@poke_maps_api.get("/maps/{map_id}")
async def get_a_map(map_id: int):
    map1 = await PokeMap.get(id=map_id)
    return wrap_response(map1.__dict__)


# @poke_maps_api.get("/try_a_map")
# async def try_a_map():
#     m1 = PokeMap(name="test1", width=3, height=2)
#     print(m1)
#     m1.cells[0][0] = Cell("grass")
#     m1.set_cell("sea", 0, 1)
#     m1.set_cell('sea', 1, 2)
#     await m1.save()
#     return m1


@poke_maps_api.post("/maps/")
async def create_a_map(name: str, width: int, height: int):
    map1 = await PokeMap.create(name=name, width=width, height=height)
    # return map1
    return wrap_response(map1.__dict__)


class MapIn(BaseModel):
    name: str
    width: int
    height: int
    # cells: list[list[int]]  # not_todo 验证cells满足width and height


@poke_maps_api.put("/maps/{map_id}")
async def put_a_map(map_id: int, map_in: MapIn):
    """修改地图尺寸"""
    m1 = await PokeMap.get(id=map_id)
    await m1.update_from_dict(map_in.model_dump())
    m1.make_void_cells()  # 修改尺寸直接重新初始化
    await m1.save()
    return wrap_response(m1.__dict__)


@poke_maps_api.put("/cell/{map_id}")
async def put_a_cell(map_id: int, x: int, y: int, value: str):
    """通过map_id和二维定位修改格子类型"""
    m1 = await PokeMap.get(id=map_id)
    cells = m1.get_cells()
    cells[x][y] = CellEnum[value].value
    m1._cells = json.dumps(cells)
    # print(f"type: {cells}")
    await m1.save()
    return wrap_response(m1.__dict__)

