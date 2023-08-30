"""
FastAPI based API backend code
Author: Parth Shastri
"""
import os
import json
from enum import Enum
import re
from utils import docai_call, PROJECT_ID, doc_to_csv
from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from google.oauth2 import id_token
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from google.cloud import documentai_v1 as docai
import pandas as pd
import uvicorn
import requests
import watermark


templates = Jinja2Templates(directory="templates")

app = FastAPI(title="Motor invoice extractor")

# set up the static files like css , js and images etc.
static_files_dir = os.path.join(os.path.dirname(__file__), "static")
# print(static_files_dir)
app.mount("/static", StaticFiles(directory=static_files_dir), name="static")

# setup cross-origin resource sharing
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# setting the oauth credentials setup from google cloud
configFile = "config/app.setting.json"

with open(configFile, "r", encoding="utf-8") as fp:
    configuration = json.load(fp)


# setting the application default credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = configuration["GCP"]["Credentials"]


class dropdownChoices(str, Enum):
    honda = "honda"
    toyota = "toyota"
    tvs = "tvs"
    kia = "kia"
    hyundai = "hyundai"


@app.get("/", response_class=HTMLResponse)
async def insurance_extraction(request: Request):
    """
    Render the document extraction index page
    """
    # username = request.session.get("name")
    return templates.TemplateResponse(
        "index.html", context={"request": request, "username": "User"}
    )


@app.get("/ind", response_class=HTMLResponse)
async def main(request: Request):
    """
    Render the login html template in the templates folder
    """
    return templates.TemplateResponse("login.html", context={"request": request})


@app.post("/data/", response_class=FileResponse)
async def read_data():
    file_path = "artifacts/temp_csv.csv"
    response = FileResponse(file_path, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=downloaded_file.csv"
    return response


@app.post("/predict")
async def predict_fn(document: UploadFile = File(...), parser: dropdownChoices = Form(dropdownChoices.honda)):
    """
    The route responsible to predict the Insurance document fields according to requirements
    """
    # print(document.filename)
    # print(document.content_type)

    # if document.content_type != "application/pdf":
        # return JSONResponse({"message": "PDF not detected, Please upload a pdf file!"})

    document_contents = await document.read()
    print(document.filename)
    ocr_document = docai_call(document.filename, parser=parser, file_contents=document_contents)

    #convert the response entities to csv
    csv_data = doc_to_csv(ocr_document)
    temp_location = "artifacts/temp_csv.csv"
    csv_data.to_csv(temp_location)

    print(csv_data.to_json(orient="index"))
    # return HTMLResponse(csv_data.to_html())
    return RedirectResponse(url="/data/")


if __name__ == "__main__":
    print(
        watermark.watermark(
            author="Parth Shastri",
            packages="fastapi, spacy, fasttext, google-cloud-aiplatform",
            python=True,
        )
    )
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080,
    )
