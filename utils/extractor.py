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

Your task is to extract clearly stated facts. These may include standard mortgage application fields as well as additional personal, informal, or financial details.

Use one of the following official 1003 field names **if there is a clear match**:

{field_list_string}

If no match applies, generate a descriptive and concise custom field name (e.g., "Pet Name", "Spiritual Advisor", "Bitcoin Holdings").

---

Assign a confidence score for each field based on how clearly it was stated:

- 1.0 → directly and explicitly mentioned
- 0.7 → implied or casually referenced
- 0.5 or lower → vague, uncertain, or inferred

You must NOT assign 1.0 unless the value is directly, clearly, and confidently stated without any uncertainty, hesitation, or speculation.

For example:
- “I need a loan of $300,000” → 1.0
- “Maybe something like $300,000” → 0.5 or lower
- “I used to work at Dell” → 0.6 (for previous employer)

Return only the final output in this JSON format — no extra text:

{{
  "fields": [
    {{
      "field_name": "Loan Amount",
      "field_value": "$350,000",
      "confidence_score": 1.0
    }},
    {{
      "field_name": "Pet Name",
      "field_value": "Luna",
      "confidence_score": 0.6
    }},
    {{
      "field_name": "Spiritual Advisor",
      "field_value": "my advisor",
      "confidence_score": 0.5
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
        response = model.generate_content(prompt, generation_config={"temperature": 0.4})
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
            line = f"{idx} {field['field_name']}: {field['field_value']} (Confidence: {field['confidence_score']:.2f})"
            numbered_output.append(line)

        return {"formatted_output": numbered_output}

    except Exception as e:
        return {
            "error": "Failed to parse model response",
            "details": str(e),
            "raw_response": response.text if 'response' in locals() else ""
        }
