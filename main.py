import asyncio
import os
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

CSV_FILE_PATH = "yarn_rates.csv"
HTML_FILE_PATH = "index.html"

@app.get("/")
async def get():
    # 1. Check if the HTML layout file exists on disk
    if os.path.exists(HTML_FILE_PATH):
        with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    return HTMLResponse("<h2>Error: index.html template file not found.</h2>", status_code=404)

@app.websocket("/ws/prices")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if os.path.exists(CSV_FILE_PATH):
                try:
                    df = pd.read_csv(CSV_FILE_PATH)
                    df.columns = df.columns.str.strip()
                    
                    dataset_json = df.to_dict(orient="records")
                    await websocket.send_json(dataset_json)
                except Exception as e:
                    print(f"Error processing CSV data: {e}")
            else:
                print(f"Warning: CSV file not found at {CSV_FILE_PATH}")
            
            # Broadcast updates every 3 seconds
            await asyncio.sleep(3)
            
    except WebSocketDisconnect:
        print("Web browser client disconnected. Stopping the real-time loop.")

