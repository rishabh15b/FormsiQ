
import requests
import json
import pandas as pd
import os

if not os.path.exists("test_result"):
    os.makedirs("test_result")
    
sample_transcripts = [
    "Hi, my name's Daniel. I'm not sure what I qualify for yet. I might need a loan but haven't figured out the amount. Oh, and my turtle's name is Flash—he's been with me for 10 years!",
    "Good afternoon, I'm Michael Taylor. I was born on May 12, 1980, and I want to refinance my house at 123 Ocean View Blvd. I work at IBM and earn roughly $9,500 per month.",
    "Hi, I'm Laura. I might be interested in getting a home loan... maybe somewhere around $400,000? I worked at Apple a while ago but recently switched fields. Just exploring options for now.",
    "Hi there. I'm Emily. I've been looking into mortgages, but I don't have income details right now. I just wanted to learn about the application process. Not ready to proceed yet.",
    "Yes, my name's George. I own a rental property at 55 Birch Lane bringing in about $1,200 monthly. I'm looking to apply for a $150,000 loan to help with some home renovations.",
    "Hey, I've been thinking about buying a place. Don't really know where to start or how much I'd need. Just wanted to ask a few questions before jumping in.",
    "Hey, this is Jessica Lee. I'd like to discuss getting a mortgage. My SSN is 123-45-6789 and I'm hoping to get a loan for $325,000. I'm employed at Citibank and take home about $7,000 monthly.",
    "Hi, I'm Robert Gray calling about a mortgage application. I'm looking to borrow $280,000 for a home purchase. I work full-time at FedEx and earn around $6,200 per month.",
    "Hello, I'm Sarah. A friend told me about your services. I haven't settled on an amount, but they got approved for $300,000. I might look into something similar.",
    "Hi there, this is Priya Nair. I run my own consulting business—Nair Consulting. I'm self-employed and want to apply for a $200,000 mortgage. I've been in this line of work for about 5 years."
]

results = []

for idx, transcript in enumerate(sample_transcripts):
    try:
        response = requests.post(
            "http://localhost:8000/extract-fields",
            json={"transcript": transcript}
        )
        data = response.json()
        results.append({
            "test_case": idx + 1,
            "transcript": transcript,
            "extracted_fields": data.get("fields", []),
            "error": data.get("error", None)
        })
    except Exception as e:
        results.append({
            "test_case": idx + 1,
            "transcript": transcript,
            "extracted_fields": [],
            "error": str(e)
        })

# Save results to CSVx
df = pd.DataFrame(results)
df.to_csv("test_result/test_results.csv", index=False)
print("Results: test_results.csv")
