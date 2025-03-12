from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Text to Video API Running on Render"}

@app.get("/generate")
def generate_video(prompt: str):
    model = pipeline("text-to-video", model="runwayml/stable-video-diffusion")
    video = model(prompt)
    return {"video_url": video}
