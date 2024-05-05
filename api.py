import os
import databases
from config import DB_URI
from datetime import datetime



from typing import Optional

database = databases.Database(DB_URI)


from fastapi import FastAPI, Request

app = FastAPI()



async def insert_into_table(database, table_name ,values_in_dict):
    """
    This function will insert value in table using dictionary
    Parameters:
    database:  database object after connecting to db 
    table_name: 
    values_in_dict: dictionary where keys is column name and value (where key will be value)

    returns:
    """
    all_value_keys = list(values_in_dict.keys())

    suf_res = []
    temp_suf_res = []
    for idx, i in enumerate(all_value_keys):
        if len(all_value_keys) - 1 == idx:
            suf_res.append(f"`{i}`")
            temp_suf_res.append(i)
        else:
            suf_res.append(f"`{i}`, ")
            temp_suf_res.append(i + ", ")

    pre_res = list(map(lambda x: ":" + x, temp_suf_res))

    query = f"INSERT INTO {table_name} ("
    query = query + "".join(suf_res) + ") VALUES (" + "".join(pre_res) + ")"

    await database.execute(query=query, values=values_in_dict)



# Function to connect to the database
@app.on_event("startup")
async def connect_to_database():
    await database.connect()
    print("Connected to database")

@app.get("/get_data/")
async def root():
    return {"message": "Hello World"}


@app.post("/post_data/")
async def post_data(info: Request):
    value_dict = await info.json()

    # await database.connect()
    if value_dict is not None:
        formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        value_dict["dt"] = formatted_date
        
        pk = await insert_into_table(database, "hackupc.dht11" , value_dict )
        
        return {"pk": pk}
    else:
        return {"message": f"Received temperature"}