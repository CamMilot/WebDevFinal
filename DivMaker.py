import json
import pandas as pd
import psycopg2
from markupsafe import Markup
import re
from sqlalchemy import create_engine

class DivMaker:
    items = []
    postgresArgs = ''
    tableName = ''
    def __init__(self,tableName,postgresArgs) -> None:
        self.postgresArgs = postgresArgs
        self.tableName = tableName
        self.conn = psycopg2.connect(postgresArgs)
        self.cursor = self.conn.cursor(tableName)
        self.conn.autocommit = False
        pd.options.mode.copy_on_write = True
        self.cursor.execute(f'SELECT * FROM {tableName}')
        result = self.cursor.fetchall()
        columnNames = [desc[0] for desc in self.cursor.description] 
        self.items = pd.DataFrame(result)
        self.items.columns = columnNames

    def updateDB(self):

        #engine = create_engine('postgresql+psycopg2://postgres:pass@localhost/postgres')
        #upsert_df(self.items,self.tableName,engine=engine)
        pass

        
    def close(self):
        self.conn.close()
        self.cursor.close()

    def open(self):
        self.conn = psycopg2.connect(self.postgresArgs)
        self.cursor = self.conn.cursor(self.tableName)





    def createDivCart(self,cookie,request):
        div =''
        total = 0
        if not cookie: cookie = "{ }"
        cookie = cookie.replace("'",'"')
        print(cookie)
        cookie = json.loads(cookie)
        for item in cookie:
            quantity = cookie[item]
            row = self.items.loc[int(item)]
            saleAmnt = row['saleamnt']
            priceSale = int(row['price'])*((100-saleAmnt)*.01)
            price = '{0:.2f}'.format(row['price'])
            priceSale = '{0:.2f}'.format(priceSale)
            if bool(row['sale']):
                price = f'<s> ${price}</s><font color="#8B0000">  ${priceSale} </font> <br> <font color = "gray" size -= 2>{saleAmnt}% Off</font>'
            else:
                price = '$'+price 
            link = row['link']
            removeForm = f'<form method="post" target="_self"> <input type="hidden" id="purchase" name="purchase" value="False"><input type="hidden" id="itemID" name="itemID" value="{item}"><input type="submit" value="Remove">'
            item = row['name']
            inlineCSS = f'style="background-image:url({link})"'
            innerDiv = f'<div class="contentCart" >{item} <br> {price} </div>'   
            div+= f'<div class="saleitem" {inlineCSS}>{innerDiv}<div class="quantity">Ammount:{quantity}<br>{removeForm}</div></div>'
            total += int(quantity)*float(re.findall("\d+\.\d+", price)[-1])
        totalInput = f'<input type="hidden" id="total" name="total" value="{total}">'
        purchaseForm = f'<form method="post" target="_self"> <input type="hidden" id="purchase" name="purchase" value="True"><input type="hidden" id="itemID" name="itemID" value="None">{totalInput}<input type="submit" value="PURCHASE">'
        
        div = Markup(div + "<br><br><br>total $" + str(total) + "<br>" + purchaseForm)
        return div

    def createDivHome(self,request):
        div = ''
        for index,row in self.items.iterrows():
            if row['quantity'] < 1:
                continue
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

    def createDivItem(self,itemid):
        row = self.items.loc[itemid]
        div = ''
        price = row['price']
        item = row['name']
        link = row['link']
        sale = row['sale']
        quantity = row['quantity']
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
        formLabel = '<label for="cValue">Quantity:</label><br>'
        formInput = f'<input type="number" id="quantity"  name="quantity" min="1" max="{quantity}">'
        formSubmit = '<input type="submit" value="">'
        innerForm = f'<form method="post" target="_self" class="formContent">{formLabel}{formInput}{formSubmit}<form><br>'
        innerDiv+= innerForm
        div+= f'<div class="saleitem" {inlineCSS}>{innerDiv}</div>'
        div = Markup(div)
        return div


