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


columnNames = [desc[0] for desc in cursor.description] 




app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

linebreaks = Markup('<br>'*10)


items = pd.DataFrame(result)
items.columns = columnNames




def createDivHome(items,request):
    div = ''
    for index,row in items.iterrows():
        saleAmnt = row['saleamnt']
        priceSale = int(row['price'])*((100-saleAmnt)*.01)
        price = '{0:.2f}'.format(row['price'])
        priceSale = '{0:.2f}'.format(priceSale)
        if bool(row['sale']):
            price = f'<s> ${price}</s><font color="#8B0000">  ${priceSale} </font> <br> <font color = "gray" size -= 2>{saleAmnt}% Off</font>'
        else:
            price = '$'+price 
        link = row['link']
        item = row['name']
        inlineCSS = f'style="background-image:url({link})"'
        innerDiv = f'<a class="content" href="{str(request.url)}items/{row[0]}">{item} <br> {price} </a>'   
        innerLink = f'<a class="salelink" href="{str(request.url)}items/{row[0]-1}"></a>'

        div+= f'<div class="saleitem" {inlineCSS}>{innerLink}{innerDiv}</div>'
    div = Markup(div)
    return div

def createDivItem(items,itemid):
    row = items.loc[itemid]
    div = ''
    price = row['price']
    item = row['name']
    link = row['link']
    sale = row['sale']
    saleAmnt = row['saleamnt']
    priceSale = int(price)*((100-saleAmnt)*.01)
    price = '{0:.2f}'.format(price)
    priceSale = '{0:.2f}'.format(priceSale)
    if bool(sale):
        price = f'<s> ${price}</s><font color="#8B0000">  ${priceSale} </font> <br> <font color = "gray">{saleAmnt}% Off</font>'
    else:
        price = '$'+price
        
    inlineCSS = f'style="background-image:url({link})"'
    innerDiv = f'<div class="content" >{item} <br> {price} </div>'   

    div+= f'<div class="saleitem" {inlineCSS}>{innerDiv}</div>'
    div = Markup(div)
    return div





@app.get("/")
def read_root(request: Request):
    div = createDivHome(items,request)
    return templates.TemplateResponse("main.html",{"request":request,"test":div,"linebreak":linebreaks})


@app.get("/items/{item_id}")
def read_item(request: Request, item_id: int, q: Union[str, None] = None):
    div = createDivItem(items,item_id)
    return templates.TemplateResponse("item.html",{"request":request,"test":div,"linebreak":linebreaks})
