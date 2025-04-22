from decimal import Decimal
from settings import custom


def subscribe_content_cost(content: str) -> Decimal:
    """
    计算订阅章节消耗
    :param content:
    :return:
    """
    cost_rate = custom["subscribe_content_cost_rate"]  # 100
    decimal_places = custom["decimal_places"]  # 2
    subscribe_min_content = custom["subscribe_min_content"]  # 200
    subscribe_min_cost = custom["subscribe_min_cost"]  # "0.01"
    length = len(content)
    if length < subscribe_min_content:
        return Decimal(subscribe_min_cost)
    else:
        temp = round(length / cost_rate, decimal_places)
        return Decimal(str(temp))
