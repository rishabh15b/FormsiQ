import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from utils.field_map import FIELD_NAME_MAP

# Load environment variables from .env file
# Ensure you have a .env file with the following content:
# GEMINI_API_KEY=your_api_key_here
load_dotenv()

# Initialize the Generative AI model
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Ensure the model is set to the correct version
model = genai.GenerativeModel('models/gemini-1.5-flash')

# Define the log file for unmapped fields
LOG_FILE = "unmapped_fields_log.txt"

def extract_fields_from_transcript(transcript: str):
    # Clear previous unmapped field log
    with open(LOG_FILE, "w") as f:
        f.write("")

    allowed_fields = sorted(set(FIELD_NAME_MAP.values()))
    field_list_string = "\n- " + "\n- ".join(allowed_fields)

    # Prepare the prompt for the model
    # The prompt is designed to instruct the model on how to extract fields from the transcript
    prompt = f"""
You are an AI assistant that extracts structured data from a mortgage-related conversation transcript.

Your goal is to identify clearly stated facts relevant to a mortgage application. These may include both standard 1003 form fields and additional personal or informal details.

Use one of the following official 1003 field names **if there is a clear match**:

{field_list_string}

If no match applies, generate a clear and concise custom field name (e.g., "Pet Name", "Spiritual Advisor", "Bitcoin Holdings").

---

For each field, assign a **confidence_score** between **0.0 and 1.0** using these guidelines:

- Start at 1.0 if the value is **explicitly stated** in a clear, confident, assertive sentence:
    - e.g., “I am applying for a loan of $300,000.”
    - e.g., “I work at Wells Fargo.”
    - e.g., “My name is Sarah.”

- Reduce confidence to **0.8 - 0.95** if the value is mostly clear but lacks emphasis or full context:
    - e.g., “I think I'll need about $250,000.”
    - e.g., “I'm probably working at Dell.”

- Drop to **0.5 - 0.7** if phrasing is hesitant, indirect, or speculative:
    - e.g., “Maybe something like $200,000.”
    - e.g., “I used to be at JPMorgan, I think.”

- Use **< 0.5** if the mention is vague, hypothetical, or highly uncertain:
    - e.g., “Someone said I might need a mortgage.”
    - e.g., “I'm still figuring out income.”

Score based on **sentence structure, language certainty, and proximity of value to context**. Think carefully and grade naturally — no need to round to 0.5, 0.7, or 1.0. Use any float between 0.0 and 1.0.

Return only a clean JSON response. No extra commentary.

{{
  "fields": [
    {{
      "field_name": "Loan Amount",
      "field_value": "$300,000",
      "confidence_score": 0.93
    }},
    {{
      "field_name": "Pet Name",
      "field_value": "Luna",
      "confidence_score": 0.57
    }},
    {{
      "field_name": "Spiritual Advisor",
      "field_value": "my advisor",
      "confidence_score": 0.50
    }}
  ]
}}

Transcript:
\"\"\"{transcript}\"\"\"
"""

    # Generate content using the model
    # The model is expected to return a JSON response with the extracted fields
    # The response is then parsed to extract the relevant fields and their corresponding confidence scores
    # The function also handles any exceptions that may occur during the process
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.3})
        # print("Response:", response.text)
        # Extract the JSON part from the response
        start = response.text.find("{")
        end = response.text.rfind("}") + 1
        cleaned = response.text[start:end]
        data = json.loads(cleaned)
      
        transcript_lower = transcript.lower()
        filtered_fields = []
        unmapped_fields = set()

        # Iterate through the fields in the model's response

        for field in data.get("fields", []):
            raw_name = field.get("field_name", "").strip()
            std_name = FIELD_NAME_MAP.get(raw_name, raw_name)
            value = str(field.get("field_value", "")).strip()
            score = field.get("confidence_score", 0)

            # Only allow if std_name is part of official 1003 fields
            if std_name in FIELD_NAME_MAP.values():
                # if value.lower().replace(",", "").strip() in transcript_lower:
              filtered_fields.append({
                  "field_name": std_name,
                  "field_value": value,
                  "confidence_score": score
              })
            else:
                unmapped_fields.add(std_name)

        # Save unmapped field names to log
        if unmapped_fields:
            with open(LOG_FILE, "w") as f:
                for name in sorted(unmapped_fields):
                    f.write(f"{name}\n")

        numbered_output = []
        for idx, field in enumerate(filtered_fields, start=1):
            line = f"{idx}{'.'} {field['field_name']}: {field['field_value']} (Confidence: {field['confidence_score']:.2f})"
            numbered_output.append(line)

        return {"formatted_output": numbered_output}

    except Exception as e:
        return {
            "error": "Failed to parse model response",
            "details": str(e),
            "raw_response": response.text if 'response' in locals() else ""
        }
