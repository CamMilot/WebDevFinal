
# WebDevFinal

## Requirements
Python, PostgreSQL Server \
FastAPI, psycopg2, Pandas, Jinja2  \
Uvicorn, sqlAlchemy, MarkupSafe \
pydantic, python-multipart

## Final Update 4/28/24
[Website(unsecure)](www.cameronmilot.com)
Finished Website
Added option of a cart using cookies
Added generation of purchase and reciept
Cleaned up code
Hosting through home server

## Current Progress

### Demonstration
![Home Page Progress](https://i.imgur.com/XG34wuT.png)
![Sale Page Progress](https://i.imgur.com/mo4jLwj.png)

Created a main page listing all available items for sale which links to inner pages containing the specific item
### Coding Work
The back-end is in two parts, PostgreSQL and Python

 - The python/PostgreSQL portion allows me to efficiently write and get
   a csv that in the future needs to be able to be updated and possibly
   have relationships with other tables.
   
  - The python/FastAPI is the bones of the WebServer allowing users to
   actually access the content on the pages.
   - The python/HTML/CSS/Jinja2 is to create the visible portion of the website and format it.


## ~~Needs Work~~
### Coding Issues
Currently the code for retrieving the database only happens at certain intervals and when the ability to possibly purchase comes up the database will not properly update. To fix this my current plan is to run a function asynchronously and have it retrieve an updated database on an interval (5 mins) and update the WebServers items dataframe when this happens. Another factor I might consider is updating the database earlier in case of a significant change in product level (Such as someone buying all but one item)
### Other Issues
I'm not happy with the current look of the main or item page and I need to further update to enable "purchasing" of items.
Update images to actually match item description.


