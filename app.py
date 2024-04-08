from fastapi import FastAPI, Body, Query
from fastapi.responses import FileResponse
from fastapi.middleware.gzip import GZipMiddleware
from pybit.unified_trading import HTTP
from pybit.helpers import Helpers
import json
import decimal

import os

from pydantic import BaseModel

app = FastAPI()


app.add_middleware(GZipMiddleware, minimum_size=1000)

session = HTTP(
    api_key=os.environ["api_key"],
    api_secret=os.environ["api_secret"],
    testnet=False,
)


class Item(BaseModel):
    item_id: int


@app.get("/")
async def root():
    return {"message": "Hello World"}

symbol="BTCUSDT"
category="linear"

""" 
{
    "side": "LONG",
    "entry": "63816.2",
    "tp1": "64454.4",
    "tp2": "65092.5",
    "tp3": "65730.7",
    "tp4": "66368.8",
    "winrate": "52",
    "strategy": "MANUAL",
    "beTargetTrigger": "1",
    "stop": "62810.8"
}


{
    "side": "SHORT",
    "entry": "67023.9",
    "tp1": "66353.7",
    "tp2": "65683.4",
    "tp3": "65013.2",
    "tp4": "64342.9",
    "winrate": "51.03",
    "strategy": "MANUAL",
    "beTargetTrigger": "1",
    "stop": "67864.7"
}
"""

# Changing mode and leverage: 
def set_mode():
    try:
        resp = session.switch_margin_mode(
            category='linear',
            symbol=symbol,
            tradeMode=mode,
            buyLeverage=leverage,
            sellLeverage=leverage
        )
        print(resp)
    except Exception as err:
        print(err)


@app.post("/webhook")
async def webhook(data: str = Body(), secret: str = Query(None)):
    if os.environ["client_secret"] != secret:
        print("secret")
        return {"nice"}

    webhookData = json.loads(data)

    leverage = "17.5"
    order_qty = "0.01"
    dorder_qty = 0.01

    side = webhookData["side"]
    entry = webhookData["entry"]
    dentry = decimal.Decimal(webhookData["entry"])
    tp1 = webhookData["tp1"]
    tp2 = webhookData["tp2"]
    tp3 = webhookData["tp3"]
    tp4 = webhookData["tp4"]
    winrate = webhookData["winrate"]
    dwinrate = decimal.Decimal(webhookData["winrate"])
    stop = webhookData["stop"]
    dstop = decimal.Decimal(webhookData["stop"])
    distance = (dentry * 100 / dstop if side == "LONG" else dstop * 100 / dentry) - 100
    trailing = dentry - dstop if side == "LONG" else dstop - dentry


    print("Winrate")
    print(winrate)
    print("Distance")
    print(distance)

    if dwinrate < 50:
        print("Winrate low")
        return {"nice"}

    if distance > 2.2:
        print("distance to high")
        return {"nice"}
    


    print("Cancel all active orders & positions")
    Helpers(session).close_position(category=category, symbol=symbol)

    resp = session.place_order(
        category='linear',
        symbol=symbol,
        side='Buy' if side == "LONG" else 'Sell',
        orderType='Market',
        qty=order_qty,
        stopLoss=stop,
        slTriggerBy='MarkPrice'
    )

    print(resp)

    resp = session.place_order(
        category='linear',
        symbol=symbol,
        side='Buy' if side == "SHORT" else 'Sell',
        orderType='Limit',
        qty=dorder_qty*0.4,
        closeOnTrigger=true,
        timeInForce="PostOnly",
        positionIdx=0,
        price=tp1)
    
    print(resp)

    resp = session.place_order(
            category='linear',
            symbol=symbol,
            side='Buy' if side == "SHORT" else 'Sell',
            orderType='Limit',
            qty=dorder_qty*0.3,
            closeOnTrigger=true,
            timeInForce="PostOnly",
            positionIdx=1,
            price=tp2)

    print(resp)

    resp = session.place_order(
            category='linear',
            symbol=symbol,
            side='Buy' if side == "SHORT" else 'Sell',
            orderType='Limit',
            qty=dorder_qty*0.2,
            closeOnTrigger=true,
            timeInForce="PostOnly",
            positionIdx=2,
            price=tp3)

    print(resp)

    resp = session.set_trading_stop(
    category=category,
    symbol=symbol,
    takeProfit=null,
    stopLoss=null,
    tpTriggerBy=null,
    slTriggerBy=null,
    trailingStop=str(trailing),
    activePrice=tp1,
    positionIdx=3
    )

    """

    resp = session.set_leverage(
        category=category,
        symbol=symbol,
        buyLeverage=leverage,
        sellLeverage=leverage
    )
    print(resp)
    
     resp = session.place_order(
                category='linear',
                symbol=symbol,
                side='Buy' if side == "LONG" else 'Sell',
                orderType='Market',
                qty=order_qty,
                stopLoss=stop,
                slTriggerBy='Market'
            ) """
    
    # print(resp)

    """ 
    resp = session.place_order(
            category='linear',
            symbol=symbol,
            side='Buy' if side == "SHORT" else 'Sell',
            orderType='Limit',
            qty=dorder_qty*0.4,
            closeOnTrigger=true,
            timeInForce="PostOnly",
            positionIdx=0,
            price=tp1)
    print(resp)

    resp = session.place_order(
            category='linear',
            symbol=symbol,
            side='Buy' if side == "SHORT" else 'Sell',
            orderType='Limit',
            qty=dorder_qty*0.3,
            closeOnTrigger=true,
            timeInForce="PostOnly",
            positionIdx=1,
            price=tp2)

    print(resp)

    resp = session.place_order(
            category='linear',
            symbol=symbol,
            side='Buy' if side == "SHORT" else 'Sell',
            orderType='Limit',
            qty=dorder_qty*0.2,
            closeOnTrigger=true,
            timeInForce="PostOnly",
            positionIdx=2,
            price=tp3)

    print(resp)
        
    resp = session.place_order(
            category='linear',
            symbol=symbol,
            side='Buy' if side == "SHORT" else 'Sell',
            orderType='Limit',
            qty=dorder_qty*0.1,
            closeOnTrigger=true,
            timeInForce="PostOnly",
            positionIdx=3,
            price=tp4)


    print(resp)

    resp = session.set_trading_stop(
    
            )
    
    """

    print(data)
    return {"nice"}