from enum import Enum


class UpstoxTools(str, Enum):
    BUY_STOCK = "buy_stock"
    SELL_STOCK = "sell_stock"
    PLACE_AMO_ORDER = "place_amo_order"
    GET_PORTFOLIO = "get_portfolio"
    GET_FUNDS = "get_funds"
    CANCEL_ORDER_BY_ID = "cancel_order_by_id"
