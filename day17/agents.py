import os
from crewai import Agent
from langchain_community.llms import Ollama
from tools import get_search_tool

llm = Ollama(
    model = "ollama/llama3.2",
    base_url="http://localhost:11434",
    temperature = 0.7
)

search_tool = get_search_tool()
researcher_tools = [search_tool] if search_tool else []


def create_researcher():
    return Agent(
        role="Senior Research Analyst",
        goal="Uncover accurate, comprehensive information about {topic} from reliable sources",
        backstory="""You are a seasoned research analyst with expertise in gathering 
        and synthesizing information from diverse sources. You have 15 years of experience 
        in investigative research across technology, science, and current affairs.
        You are known for your ability to separate fact from opinion, identify key trends,
        and present balanced perspectives. You never guess — if you don't know, you say so.""",
        llm=llm,
        tools=researcher_tools,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
        # max_iter = agent kitni baar tool call karke retry karega
        # Default 25 hai — bahut slow ho sakta hai. 5 realistic hai.
    )


def create_writer():
    return Agent(
        role="Expert Content Writer",
        goal="Transform research findings into an engaging, well-structured article about {topic}",
        backstory="""You are a senior content writer with a background in science journalism 
        and digital media. You have written for major publications and know how to take dense 
        research and turn it into compelling, readable content. 
        You structure articles with clear headings, engaging hooks, and smooth transitions.
        You write for a general educated audience — smart but not specialist.""",
        llm=llm,
        tools=[],
        # Writer ko tools nahi chahiye — sirf research output milega
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def create_editor():
    return Agent(
        role="Chief Editor",
        goal="Polish the article about {topic} to publication quality",
        backstory="""You are a chief editor with 20 years of experience at top-tier publications.
        You have an eye for clarity, flow, and accuracy. You catch factual inconsistencies,
        fix awkward phrasing, ensure the tone is consistent throughout, and make sure 
        the article has a strong opening hook and a memorable conclusion.
        You provide specific, actionable improvements — not vague feedback.""",
        llm=llm,
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
