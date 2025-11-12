from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from transformers import pipeline

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
        You are a SEO expert with 10 plus years in experience desinging Seo optimized pages.</s>
        You how have to generate seo metadata for a product page in this EXACT format:
        TITLE: [ 60 characters SEO title ]
        DESCRIPTION: [ 155 characters seo metadata description ]
        KEYWORDS: [keyword1, keyword2, keyword3]
        <|user|>
        Product title: {req.title}
        Product description: {req.description}
        <|assistant|>
    """
    result = generator(
        promt,
        max_new_tokens=250, # Number of tokens he is going to return to me
        temperature=0.5, # Scale for anwer creativiti, 0 - Least creative (Strait to the points), 1 - Super Creative (Can give you additional data not connected to current topic)
        top_p=0.9, # Decides the rate of complex words being included in the text
        do_sample=True, # Samples previous tokens to decide the following ones
        repetition_penalty=1.2 # Negatively score repeated words
    )[0]["generated_text"]

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=3001)