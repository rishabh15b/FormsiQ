import streamlit as st
import requests
from utils.sample_prompts import sample_transcripts

st.set_page_config(page_title="FormsiQ", layout="wide")
st.title("FormsiQ - Mortgage Transcript Field Extractor")

st.markdown("This tool extracts structured 1003 form data from a mortgage-related call transcript.")

# Initialize session state for transcript
if "transcript" not in st.session_state:
    st.session_state.transcript = ""

# Sidebar for sample input
st.sidebar.title("Sample Input")
st.sidebar.markdown("Select a sample transcript to test the model's performance.")
st.sidebar.markdown("**Note:** The model may not always extract the correct fields. Please verify the results.")
st.sidebar.markdown("**⚠️ Important:** The model may hallucinate or misinterpret information. Always double-check the extracted fields.")
st.sidebar.subheader("Test Transcript")
selected_prompt = st.sidebar.selectbox(
    "Choose a sample input:",
    ["(None)"] + sample_transcripts,
    key="sample_select"
)

# If a sample is selected, load it into the main input area 
st.session_state.transcript = ''
if selected_prompt != "(None)":
    st.session_state.transcript = selected_prompt

# Main input area
st.subheader("Input Transcript")
st.markdown("You can also paste or edit the transcript directly below.")
st.subheader("Transcript")
st.session_state.transcript = st.text_area(
    "Paste or edit the transcript below:",
    value=st.session_state.transcript,
    height=200
)

# Extract button
st.markdown("### Extract Fields")
st.markdown("Click the button below to extract fields from the transcript.")
if st.button("Extract Fields"):
    if not st.session_state.transcript.strip():
        st.warning("Please enter or select a transcript.")
    else:
        with st.spinner("Processing..."):
            try:
                response = requests.post(
                    "http://localhost:8000/extract-fields",
                    json={"transcript": st.session_state.transcript}
                )
                result = response.json()

                if "fields" in result:
                    st.subheader("Extracted Fields")
                    for field in result["fields"]:
                        # st.write(f"{field['field_name']}: {field['field_value']} (Confidence: {field['confidence_score']})")
                        st.json(field)
                else:
                    st.error("No fields were extracted.")
                    st.json(result)

                # # Read and display unmapped fields in sidebar
                # try:
                #     with open("unmapped_fields_log.txt", "r") as f:
                #         unmapped = [line.strip() for line in f.readlines() if line.strip()]
                #     if unmapped:
                #         st.sidebar.markdown(f"**⚠️ {len(unmapped)} unmapped field(s) detected:**")
                #         for field in unmapped:
                #             st.sidebar.markdown(f"- {field}")
                # except FileNotFoundError:
                #     pass

            except Exception as e:
                st.error(f"API error: {e}")
