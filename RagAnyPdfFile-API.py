from fastapi import FastAPI, File, Form, UploadFile
from typing import Optional 
import io
from pydantic import BaseModel
from RagAnyPdfFile import RagAnyPdfFile
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your UI's URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# This handles your JSON/Form logic
class ChatRequest(BaseModel):
    user_query: str
    session_id: Optional[str] = "default_session"

@app.post("/uploadfile/")
async def chat_with_pdf(
    file: UploadFile = File(...),
    user_query: str = Form(...),
    session_id: Optional[str] = Form("default_session")
):
    if file is not None and file.size > 0:
        await file.seek(0) 
        contents = await file.read()
        # 2. Call your RagAnyPdfFile function with the file bytes and user query    
        response = RagAnyPdfFile(user_query, contents, file.filename)

# 3. Extract text from the response object
    final_text = response.content if hasattr(response, 'content') else str(response)
    #final_text = str(contents[:1000]) + " | Type: " + str(type(contents)) + " | Length: " + str(len(contents))  # Placeholder: Just return the first 100 bytes as a string for now
    return {"filename": file.filename, "response": final_text}
