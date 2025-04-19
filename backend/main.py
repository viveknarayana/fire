from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic model for request body
class FrameData(BaseModel):
    frame_number: int
    image_data: str  # base64-encoded image data (data URL format)
    timestamp: float

@app.post("/test")
async def receive_data(data: FrameData):
    print(f"Received frame {data.frame_number} at {data.timestamp}")
    # You could decode and save image_data if needed here
    return {"message": "Frame received", "frame": data.frame_number}
