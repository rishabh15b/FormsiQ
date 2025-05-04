from fastapi import FastAPI
from pydantic import BaseModel
from utils.extractor import extract_fields_from_transcript
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
    
app.add_middleware(
    # CORSMiddleware is used to enable Cross-Origin Resource Sharing (CORS) for the FastAPI application.
    # This allows the API to be accessed from different origins, which is useful for frontend applications.

    CORSMiddleware,
    # The `allow_origins` parameter specifies which origins are allowed to access the API.
    allow_origins=["*"],
    # The `allow_credentials` parameter allows cookies and HTTP authentication to be included in the requests.
    allow_credentials=True,
    # The `allow_methods` parameter specifies which HTTP methods are allowed.
    allow_methods=["*"],
    # The `allow_headers` parameter specifies which headers are allowed in the requests.

    allow_headers=["*"],
)
# The `TranscriptInput` class is a Pydantic model that defines the structure of the input data for the API endpoint.
class TranscriptInput(BaseModel):
    transcript: str

# The `extract_fields` function is a FastAPI endpoint that handles POST requests to the `/extract-fields` URL.
@app.post("/extract-fields")

# The function takes a `TranscriptInput` object as input and returns a dictionary with the extracted fields.
async def extract_fields(input: TranscriptInput):
    if not input.transcript.strip():
        return {"error": "Transcript is empty"}
    result = extract_fields_from_transcript(input.transcript)
    return result
