import os
import databases
from config import DB_URI
from datetime import datetime
import numpy as np

from functions import *

from typing import Optional
import pandas as pd
# Load the saved model
import xgboost as xgb


database = databases.Database(DB_URI)


from fastapi import FastAPI, Request

app = FastAPI()



# Function to connect to the database
@app.on_event("startup")
async def connect_to_database():
    await database.connect()
    print("Connected to database")


async def update_into_table():
        

    loaded_model = xgb.XGBRegressor()
    loaded_model.load_model(r'model/xgboost_model.model')

    results = await database.fetch_all("select * from hackupc.dht11")
    d = [dict(result._mapping) for result in results]
    df = pd.DataFrame.from_dict(d)
    df.set_index(['Id', 'dt'], inplace=True)  # Set 'Id' and 'dt' as index

    # Reset index to convert the multi-index into regular columns
    df.reset_index(inplace=True)

    # Group by 'Id', date, and hour, then aggregate temperature using min and max
    new_df = df.groupby([df['Id'], df['dt'].dt.date.rename('dates'), df['dt'].dt.hour.rename('hour')]).agg(
        min_temperature=('temperature', 'min'),
        max_temperature=('temperature', 'max'),
        photoresistor=('photoresistor', 'first')
    ).reset_index()

    a = []
    for i, row in new_df.iterrows():
        row_dict = row.to_dict()
            
        # Assuming you have two new data points as a list of lists or a numpy array
        new_data = np.array([[row_dict["min_temperature"], row_dict["max_temperature"]]])

        # Make predictions using the loaded model for the new data
        predictions = loaded_model.predict(new_data)
        
        a.append({"Id": row_dict["Id"], "precipitation_pred": predictions[0]})

    for res in a:
        await  update_into_table_multiple_where(database, "hackupc.dht11", res, ["Id"])

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




@app.get("/get_data/")
async def root():
    return {"message": "Hello World"}


@app.post("/post_data/")
async def post_data(info: Request):
    
    current_minute = datetime.now().minute
    
    # Check if current minute is divisible by 10
    if current_minute % 2 == 0:
        # Call your function here
        await update_into_table()
        
    value_dict = await info.json()
    # await database.connect()
    if value_dict is not None:
        formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        value_dict["dt"] = formatted_date
        pk = await insert_into_table(database, "hackupc.dht11" , value_dict )
        
        return {"pk": pk}
    else:
        return {"message": f"Received temperature None"}
