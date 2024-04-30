from datetime import date
import json
import random
import string
from typing import Optional, Union
from fastapi import FastAPI, Request, Cookie, Form, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
import uvicorn
from DivMaker import DivMaker


# Connect to postgres DB
postArgs = "dbname=postgres user=postgres password=pass"
tableName = "tabletest"

mainDM = DivMaker(tableName=tableName,postgresArgs=postArgs)

templates = Jinja2Templates(directory="templates")


linebreaks = Markup('<br>'*10)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/")
async def read_root(request: Request, cookieKey: str = Cookie(None)):
    if not cookieKey: cookieKey = ""
    div = mainDM.createDivHome(request)
    return templates.TemplateResponse("main.html",{"request":request,"test":div,"linebreak":linebreaks,"num":cookieKey.count(":")})


@app.get("/items/{item_id}")

async def read_item(request: Request,item_id: int,cookieKey: str = Cookie(None)):
    if not cookieKey: cookieKey = ""
    div = mainDM.createDivItem(item_id)
    return templates.TemplateResponse("item.html",{"request":request,"test":div,"linebreak":linebreaks,"num":cookieKey.count(":")})


@app.get("/cart/")
async def cart(request:Request, cookieKey: str = Cookie(None)):
    if not cookieKey: cookieKey = ""
    div = mainDM.createDivCart(cookie=cookieKey,request=request)
    return templates.TemplateResponse("main.html",{"request":request,"test":div,"linebreak":linebreaks,"num":cookieKey.count(":")})

@app.get("/purchased/")
async def purchased(request:Request,total: str = Cookie(None),purchased: str = Cookie(None)):
    random.seed(str(purchased) + str(date))
    orderNum = '#' + "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
    purchased = purchased.replace("'",'"')
    purchased = json.loads(purchased)
    purch = {}
    for item in purchased:
        purch[mainDM.items.loc[int(item)]['name']] = purchased[item]
        mainDM.items.loc[int(item),'quantity'] -= int(purchased[item])
    purch = str(purch).replace("{","").replace("}","").replace("'","").replace(",",f"<br>")
    purch = Markup(purch)
    print(purch)
    mainDM.updateDB()
    return templates.TemplateResponse("Reciept.html",{"request":request,"transactionID":orderNum,"total":f"${total}","items":purch})


@app.post("/cart/")
async def post_cart(itemID:Optional[str] = Form(None), total:str = Form(...),Remove: Optional[str] = Form(None),Purchase: Optional[str] = Form(None),cookieKey: str = Cookie(None)) -> RedirectResponse:

    cookieKey = cookieKey.replace("'",'"')
    cookieKey = json.loads(cookieKey)
    if not Remove:
        response = RedirectResponse(url="/purchased/",status_code=302)
        purchased = cookieKey
        cookieKey = ""
        json.dumps(purchased)
    else:
        purchased = ""
        response = RedirectResponse(url="/cart/",status_code=302)
        cookieKey.pop(str(itemID),None)
        json.dumps(cookieKey)

    response.set_cookie(key="cookieKey",value=cookieKey,samesite="None")
    response.set_cookie(key="total",value=total,samesite="None")
    response.set_cookie(key="purchased",value=purchased)
    return response


@app.post("/items/{item_id}")
async def post_cart(item_id:int,quantity: str = Form(...), cookieKey: str = Cookie(None)) -> RedirectResponse:
    item_id = str(item_id)
    quantity = str(quantity)
    response = RedirectResponse(url="/",status_code=302)
    if not cookieKey:
        cookieKey = json.dumps({ item_id : quantity
        })
    else:
        cookieKey = cookieKey.replace("'",'"')
        cookieKey = json.loads(cookieKey)
        cookieKey[item_id] = quantity
    json.dumps(cookieKey)

    response.set_cookie(key="cookieKey",value=cookieKey,samesite="None")
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, log_level="debug",
                 limit_concurrency=50, limit_max_requests=15)