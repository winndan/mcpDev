from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp.server.sse import SseServerTransport
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP()

#### Tools ####
# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print(f"Adding {a} and {b}")
    return a + b

@mcp.tool()
def days_in_month(year: int, month: int) -> int:
    """Return the number of days in a month"""
    import calendar
    return calendar.monthrange(year, month)[1]


@mcp.tool()
def generate_ai_content(prompt: str) -> str:
    """Generate AI content based on a prompt"""
    print(f"Generating AI content for prompt: {prompt}")
    return f"AI content generated for prompt: {prompt}"

# More tools can be added here

#### Resources ####
# Add a static resource
@mcp.resource("resource://some_static_resource")
def get_static_resource() -> str:
    """Static resource data"""
    return "Any static data can be returned"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


#### Prompts ####
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


@mcp.prompt()
def debug_error(error: str) -> list[tuple]:
    return [
        ("user", "I'm seeing this error:"),
        ("user", error),
        ("assistant", "I'll help debug that. What have you tried so far?"),
    ]


app2 = FastAPI()
# Create SSE Transport for handling messages
sse = SseServerTransport("/messages")
server = mcp  # Your initialized MCP instance

# Mount the MCP server under /subapi
app2.mount("/", app=server.sse_app())

@app2.get("/hello")
async def hello():
    """A simple endpoint for testing server response."""
    return {"message": "Hello from the main FastAPI app"}

# Endpoint to handle SSE connections at /subapi/sse
@app2.get("/sse")
async def handle_sse(scope, receive, send):
    async with sse.connect_sse(scope, receive, send) as streams:
        await app2.run(streams[0], streams[1], app.create_initialization_options())

# Endpoint to handle incoming messages
@app2.post("/messages")
async def handle_messages(scope, receive, send):
    await sse.handle_post_message(scope, receive, send)
