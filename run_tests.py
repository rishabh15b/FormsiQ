
import requests
import json
import pandas as pd
import os

if not os.path.exists("test_result"):
    os.makedirs("test_result")

sample_transcripts = [
    "Hi, I'm Mark Davis. I'm applying for a mortgage of $275,000. I work for Home Depot and my monthly income is $5,800.",
    "This is Laura Chen. I think I can get a loan — maybe $300,000. I used to work at Chase but recently changed jobs. My therapist says buying now is a good idea.",
    "I'm Daniel. I earn $6,200 a month, plus some stock options and annual bonus. My loan would be $400,000. I have a car loan and some credit card debt as well.",
    "My name is Sarah Lopez. I'm not sure about the amount yet. My astrologer says I should buy in June. I keep my savings in Bitcoin. My husband might co-sign the application.",
    "Yeah, I spoke with someone about the process. Didn't decide the amount or anything. Still thinking.",
    "Good afternoon, I'm Jane Smith. I want to refinance my home. The property is at 45 Lakeview Dr, Austin. I earn $8,500 monthly and work at Capital One. I'm requesting a loan of $300,000.",
    "Hi, I'm Robert Martinez. I'm thinking about a mortgage of $280,000. I work at Lowe's and live at 890 Cypress Hill Rd. My birthdate is August 15, 1986. My dog's name is Bruno.",
    "Hello, I'm Emily Carson. I might need a loan of around $350,000. I've worked at Starbucks for about 4 years. My coach recommended I buy a place at 512 Sunset Avenue, Austin. I also get tips every week, and I share rent with my sister.",
    "My loan originator is Sarah Walker. I'm asking for a $375,000 loan to buy a new house. I work at Costco and earn $7,000 monthly.",
    "This conversation is about vacation planning and our favorite books. No financial stuff here.",
    "Hey there. I was chatting with a friend and they said I should probably look into buying a home soon. No idea how much of a loan I'd need — maybe something like $250k or so? I've done some contracting for Dell in the past.",
    "I just got a new job at Amazon and my boss is really supportive. I think I can get a loan of around $300,000. My friend said I should check out some places in Austin. I also have a pet turtle named Speedy.",
    "I spoke with my financial advisor and they suggested I might want to consider a loan of $400,000. I have some savings in stocks and bonds, but I'm not sure how much I can use for a down payment. My cousin is a real estate agent and she said the market is really hot right now.",
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
