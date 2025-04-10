from dotenv import load_dotenv
import os 
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from typing import List, Optional
load_dotenv()

# ✅ Define Tour Data Model
class Tour(BaseModel):
    name: str
    location: str
    price: float
    duration: str
    description: str

# ✅ Define AI Response Model
class ResponseModel(BaseModel):
    answer: str
    tours: Optional[List[Tour]] = None

GEMINI_API_KEY = os.getenv("API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment variables!")

model = GeminiModel("gemini-2.0-flash", provider=GoogleGLAProvider(api_key=GEMINI_API_KEY))

travel_agent = Agent(
    model=model,
    result_type=ResponseModel,
    system_prompt=(
        "You are an AI assistant for a travel agency providing information about available tours and general travel inquiries. "
        "Use the available tools to retrieve real data instead of generating responses. "
        "If a user asks about tour availability, fetch the data from the database."
    ),
)

# Use async to run the agent and retrieve results
async def main():
    response = await travel_agent.run("What did I book?")
    print(response.data)  # Access the result data

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
