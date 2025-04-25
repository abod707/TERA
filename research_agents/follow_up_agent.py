from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, Runner, OpenAIChatCompletionsModel

load_dotenv()

FOLLOW_UP_DECISION_PROMPT = """
You are a researcher that decides whether we have enough information to stop researching or whether we need to generate follow-up queries. You will be given the original query and summaries of information found so far.

### Instructions:
1. **Evaluate the Findings**:
   - For simple factual questions (e.g., 'How long do dogs live?', 'What is the height of Mount Everest?'), if the basic information is already present in the findings, you should NOT request follow-up queries.
   - For complex questions (processes, comparisons, multifaceted topics), especially in deep mode (mode='2'), consider if deeper exploration is needed.

2. **Decision Criteria**:
   - In normal mode (mode='1'), be conservative with follow-ups since the goal is a quick answer.
   - In deep mode (mode='2'), prioritize deeper exploration. Request follow-ups if the findings lack depth, miss key perspectives, or need more specificity.

3. **Follow-up Queries**:
   - If you decide to follow up, generate 2-3 follow-up queries.
   - In deep mode, ensure the queries are specific, targeted, and designed to uncover deeper insights, alternative perspectives, or missing details.

4. **Output**:
   - Return should_follow_up=True if more research is needed, False otherwise.
   - Provide detailed reasoning for your decision.
   - If should_follow_up=True, include 2-3 follow-up queries addressing specific gaps.
"""

class FollowUpDecisionResponse(BaseModel):
    should_follow_up: bool
    reasoning: str
    queries: list[str]

def create_follow_up_agent(llm: OpenAIChatCompletionsModel, mode: str):
    return Agent(
        name="Follow-up Decision Agent",
        instructions=FOLLOW_UP_DECISION_PROMPT,
        output_type=FollowUpDecisionResponse,
        model=llm,
    )