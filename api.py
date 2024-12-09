from fastapi import FastAPI
import load


app = FastAPI()

@app.get("/france_travail/verify")
async def verify():
    return {"message": "Hello World"}
