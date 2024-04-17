from typing import Union
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
import psycopg2
import pandas as pd


# Connect to postgres DB
conn = psycopg2.connect("dbname=postgres user=postgres password=pass")
tableDF = pd.read_csv('ItemTable.csv')
tableName = "tabletest"
cursor = conn.cursor()

cursor.execute(f'SELECT * FROM {tableName}')
result = cursor.fetchall()






app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

linebreaks = Markup('<br>'*10)



@app.get("/")
def read_root(request: Request):
    div = ''
    for row in result:
        item = row[1]
        price = row[2]
        link = row[4]
        sale = row[5]
        saleAmnt = row[6]
        priceSale = int(price)*((100-saleAmnt)*.01)
        price = '{0:.2f}'.format(price)
        priceSale = '{0:.2f}'.format(priceSale)
        if bool(sale):
            price = f'<s> ${price}</s><font color="#8B0000">  ${priceSale} </font> <br> <font color = "gray" size -= 2>{saleAmnt}% Off</font>'
        else:
            price = '$'+price
        inlineCSS = f'style="background-image:url({link})"'
        innerDiv = f'<a class="content" href="{str(request.url)}items/{row[0]}">{item} <br> {price} </a>'   
        innerLink = f'<a class="salelink" href="{str(request.url)}items/{row[0]-1}"></a>'

        div+= f'<div class="saleitem" {inlineCSS}>{innerLink}{innerDiv}</div>'
    div = Markup(div)
    return templates.TemplateResponse("main.html",{"request":request,"test":div,"linebreak":linebreaks})


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return result[item_id]
