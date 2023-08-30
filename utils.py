import json
import re
import pandas as pd
from google.cloud import documentai_v1 as docai
from doc_ai_ext import doc_ai_process

with open("config/app.setting.json", "r", encoding="utf-8") as fp:
    configuration = json.load(fp)

# Document AI Processor details
PROJECT_ID = configuration["GCP"]["ProjectId"]
LOCATION = configuration["GCP"]["Location"]
# PROCESSOR_ID = configuration["GCP"]["DocAIProcessorId"]


def docai_call(file_path, parser="honda", file_contents=None):
    """
    A helper function to obtain the ocr text from the doc ai processor
    """
    # mime_type="application/pdf"

    if file_path.endswith("pdf") or file_path.endswith("PDF"):
        mime_type = "application/pdf"

    elif (
        file_path.endswith("jpg")
        or file_path.endswith("jpeg")
        or file_path.endswith("JPG")
    ):
        mime_type = "image/jpeg"

    elif file_path.endswith("png") or file_path.endswith("PNG"):
        mime_type = "image/png"

    processor_id = configuration["GCP"]["DocAIProcessorId"][parser]

    if file_contents is not None:
        final_response = doc_ai_process(
            PROJECT_ID,
            LOCATION,
            processor_id,
            file_path=None,
            file_contents=file_contents,
            mime_type=mime_type,
        )

    else:
        final_response = doc_ai_process(
            PROJECT_ID, LOCATION, processor_id, file_path, mime_type=mime_type
        )
    return final_response


def preprocess_text(text):
    """
    A function to preprocess the ocr text to obtain a cleaner text
    in order to reduce the complexity of the responses of the llm.
    """

    # ocr pre process
    text = str(text).replace("\n", "  ").lower()
    text = re.sub("\W+", " ", str(text.encode("ascii", "ignore"), "utf-8").lower())

    return text


def doc_to_csv(doc : docai.Document, threshold=0.5) -> pd.DataFrame:
    ROW_ENTITIES = ['gst_percent', 'part_hsn', 'part_name', 'part_quantity', 'part_rate']
    DOC_ENTITIES = ['invoice_name', 'invoice_id', 'invoice_date','dealer_gst_number', 'painting_labour', 'total_amount']

    COLS = ['invoice_name', 'invoice_id', 'invoice_date', 'gst_percent', 'part_hsn', 'part_name',
    'part_quantity', 'part_rate', 'dealer_gst_number', 'painting_labour', 'total_amount']

    ROW_TYPE = 'invoice_row'
    THRESH = threshold

    entities = doc.entities

    rows = []
    doc_entities = {}
    for e in entities:
        if e.type == ROW_TYPE and e.confidence > THRESH:
                props = e.properties
                props = [(props.type, props.mention_text) for props in e.properties]

                row = {}
                for p_type, val in props:
                    p_type = p_type.split('/')[1]
                    if p_type in ROW_ENTITIES:
                        row[p_type] = val
                rows.append(row)
        elif e.type in DOC_ENTITIES and e.confidence > THRESH:
            doc_entities.setdefault(e.type, []).append((e.mention_text, e.confidence))
    df = pd.DataFrame.from_dict(rows)

    for name, values in doc_entities.items():
        sorted(values, key= lambda tup: tup[1])
        df[name] = values[0][0]

    present_cols = [col for col in COLS if col in df.columns]

    return df.loc[:, present_cols]
