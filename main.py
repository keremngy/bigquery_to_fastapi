from math import ceil
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import status
import secrets
import uvicorn
from google.cloud import bigquery
from google.oauth2 import service_account


if __name__ == "__main__":
    uvicorn.run("main:app", reload=False)

app = FastAPI()
security = HTTPBasic()
credentials = service_account.Credentials.from_service_account_file('APIKEY.json')
project_id = 'PROJECTID'
client = bigquery.Client(credentials= credentials,project=project_id)



class Item:
    def __init__(self, record):
        self.id = record['id']
        self.disease = record['Disease']
        self.fever = record['Fever']
        self.cough = record['Cough']
        self.fatigue = record['Fatigue']
        self.diff_breathing = record['Difficulty_Breathing']
        self.age = record['Age']
        self.gender = record['Gender']
        self.blood_preasure = record['Blood_Pressure']
        self.chol_level = record['Cholesterol_Level']
        self.date = record['Date']


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"username"
    is_correct_username = secrets.compare_digest(current_username_bytes, correct_username_bytes)
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"password"
    is_correct_password = secrets.compare_digest(current_password_bytes, correct_password_bytes)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/items")
def read_items(request: Request, skip: int = 0, limit: int = 100, username: str = Depends(get_current_username)):
    countquery = f"""SELECT COUNT(*) as total_count
        FROM `YOURTABLE`"""
    count_query = client.query(countquery)
    count_result = list(count_query.result())[0]
    total_count = count_result["total_count"]
    total_pages = ceil(total_count / limit)

    myquery = f"""SELECT * 
        FROM `YOURTABLE` 
        order by id asc
        LIMIT {limit}
        OFFSET {skip}"""
    query = client.query(myquery)
    records = [dict(row) for row in query]
    item_list = []
    for record in records:
        item = Item(record)
        item_list.append(item.__dict__)

    current_page = ceil((skip + 1) / limit)
    next_page = current_page + 1 if current_page < total_pages else None
    url = str(request.base_url)
    next_page_url = f"{url}items?skip={current_page * limit}&limit={limit}" if next_page else None

    return {
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": current_page,
        "next_page_url": next_page_url,
        "data": item_list,
    }
@app.get("/lastitems")
def read_items(skip: int = 0, limit: int = 1000, id: int = None, username: str = Depends(get_current_username)):
    countquery = f"""SELECT COUNT(*) as total_count
        FROM `YOURTABLE`"""
    count_query = client.query(countquery)
    count_result = list(count_query.result())[0]
    total_record_count = count_result["total_count"]
    myquery = f"""SELECT * 
        FROM `YOURTABLE`"""

    if id is not None:
        myquery += f" WHERE id > {id}"
    myquery += f" order by id asc LIMIT {limit} OFFSET {skip}"
    query = client.query(myquery)
    records = [dict(row) for row in query]
    item_list = []
    for record in records:
        item = Item(record)
        item_list.append(item.__dict__)
    filtered_record_count = len(item_list)
    return {
        "total_record_count": total_record_count,
        "filtered_record_count": filtered_record_count,
        "data": item_list}
