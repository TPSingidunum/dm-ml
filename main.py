from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from transformers import pipeline
import json

app =  FastAPI(title="DM-DML")

generator = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", device_map="cpu") # cpu, gpu

class SEORequest(BaseModel):
    title: str
    description: str
    brand: Optional[str] = None
    category: Optional[str] = None

class SEOResponse(BaseModel):
    seo_title: str
    seo_description: str
    keywords: List[str]
    raw: str

@app.get("/seo/generate/product")
def test(req: SEORequest):
    promt = f"""
        <|system|>
        You are a SEO expert with 10 plus years in experience desinging Seo optimized pages.
        The `title` has to be shorter than 60 words, the `desc` has to be shorter than 150 words,
        and for the key words put 5 of them.

        DO NOT FORGET THE KEY field in the generated json
        
        You now have to generate the json object containg this information in this EXACT format, no additional response needed after this:
            {{
	            "title": "EXAMPLE SEO TITLE MAX",
	            "des": "EXAMPLE SEO DESCRIPTION MAX",
	            "key": ["Example","Keywords","Here"],
            }}

        <|user|>
        Product title: {req.title}
        Product description: {req.description}
        <|assistant|>
    """
    result = generator(
        promt,
        max_new_tokens=1000, # Number of tokens he is going to return to me
        temperature=0.5, # Scale for anwer creativiti, 0 - Least creative (Strait to the points), 1 - Super Creative (Can give you additional data not connected to current topic)
        top_p=0.9, # Decides the rate of complex words being included in the text
        do_sample=True, # Samples previous tokens to decide the following ones
        repetition_penalty=1 # Negatively score repeated words
    )[0]["generated_text"]


    jsonResponse = ""
    while True:
        try:
            response = result.split("<|assistant|>")[-1].strip()
            jsonResponse = json.loads(response)
            print("-"*20)
            print("Successfully parsed response: \n" + str(jsonResponse))
            break
        except:
            print("-"*20)
            print("Response body: \n" + response)
            print("Promt him again")
            # TODO: add the failed response back and tell him to fix his mistake
            result = generator( promt, max_new_tokens=1000, temperature=0.5, top_p=0.9, do_sample=True, repetition_penalty=1)[0]["generated_text"]

    final = {}
    tempKeys = list(jsonResponse.keys())
    validKeys = ["title", "description", "keywords"]

    for i in range(len(tempKeys)):
        final[validKeys[i]] = jsonResponse[tempKeys[i]]

    return final


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=3001)