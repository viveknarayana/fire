from fastapi import FastAPI

# Create a FastAPI instance
app = FastAPI()

# Example GET endpoint
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


