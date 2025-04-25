from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, Runner, OpenAIChatCompletionsModel

load_dotenv()

QUERY_AGENT_PROMPT = """You are a helpful assistant that can generate search queries for research.
For each query, follow these steps:

1. First, think through and explain:
   - Break down the key aspects that need to be researched.
   - Consider potential challenges and how you'll address them.
   - Explain your strategy for finding comprehensive information.

2. Then generate 1 to 5 search queries based on the complexity of the input:
   - For simple queries (e.g., "What is the capital of France?"), generate 1–2 queries.
   - For moderately complex queries (e.g., "How do solar panels work?"), generate 2–3 queries.
   - For highly complex queries (e.g., "Compare the economic impacts of renewable energy adoption in Europe vs. Asia"), generate 4–5 queries.
   - Ensure queries are specific, focused on retrieving high-quality information, and cover different aspects of the topic to help find relevant and diverse information.

Always provide both your thinking process and the generated queries.
"""

class QueryResponse(BaseModel):
    queries: list[str]
    thoughts: str

def create_query_agent(llm: OpenAIChatCompletionsModel):
    return Agent(
        name="Query Generator Agent",
        instructions=QUERY_AGENT_PROMPT,
        output_type=QueryResponse,
        model=llm,
    )