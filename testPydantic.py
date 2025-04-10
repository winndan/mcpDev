import asyncio
from dotenv import load_dotenv
import os
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.mcp import MCPServerHTTP

load_dotenv()

GEMINI_API_KEY = os.getenv("API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment variables!")

model = GeminiModel("gemini-2.0-flash", provider=GoogleGLAProvider(api_key=GEMINI_API_KEY))

server = MCPServerHTTP(url='http://localhost:8000/sse')  
agent = Agent(model=model, mcp_servers=[server])  

async def main():
    print("Starting MCP servers...")
    async with agent.run_mcp_servers():
        print("MCP servers are running.")
        
        # Retry logic for handling rate limits
        max_retries = 3
        retry_delay = 22  # seconds (based on the error message)

        for attempt in range(max_retries):
            try:
                # Query 1: General query
                result = await agent.run('How many days are in March 2025?')
                print("Result:", result.data)

                # Query 2: Addition query
                result1 = await agent.run('add 10 and 1003')
                print("Result1:", result1.data)
                break  # Exit loop if successful

            except Exception as e:
                if "status_code: 429" in str(e):  # Check for rate limit error
                    print(f"Rate limit exceeded. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                else:
                    raise e  # Re-raise other exceptions

        else:
            print("Max retries exceeded. Please check your quota or try again later.")

if __name__ == "__main__":
    asyncio.run(main())
