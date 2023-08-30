"""Import the required libraries"""
import json
from google.cloud import documentai_v1 as documentai
from typing import Optional
from fastapi.responses import JSONResponse
import logging
import gc


def print_page_dimensions(dimension: documentai.Document.Page.Dimension) -> None:
    """Getting page dimension"""
    print(f"    Width: {str(dimension.width)}")
    print(f"    Height: {str(dimension.height)}")


def online_process(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
    file_contents: Optional[str] = None,
) -> documentai.Document:
    """
    Processes a document using the Document AI Online Processing API.
    """

    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

    # Instantiates a client
    documentai_client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    resource_name = documentai_client.processor_path(project_id, location, processor_id)

    # Read the file into memory
    if file_path is not None:
        with open(file_path, "rb") as file:
            file_content = file.read()

    if file_contents is not None:
        file_content = file_contents

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)

    # Use the Document AI client to process the sample form
    result = documentai_client.process_document(request=request)
    return result.document


def doc_ai_process(
    project_id,
    location,
    processor_id,
    file_path,
    mime_type="application/pdf",
    file_contents=None,
):
    # print("I am there in doc_ai_process")
    """
    Document AI extraction main function
    """
    try:
        document = online_process(
            project_id=project_id,
            location=location,
            processor_id=processor_id,
            file_path=file_path,
            mime_type=mime_type,
            file_contents=file_contents,
        )
        # Get the  response from document ai
        return document
    except Exception as err:
        logging.error(err, exc_info=True)
        return JSONResponse(
            content={"error": str(err)},
            status_code=500,
            media_type="application/json",
        )
