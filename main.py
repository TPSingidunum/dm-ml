from fastapi import FastAPI

app =  FastAPI(title="DM-DML")

@app.get("/hello")
def test():
    return "Hello"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=3001)