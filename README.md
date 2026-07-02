**80 Days Roadmap to Ai Specialist**

- Day 01 ✅ - Python 3.11+ · uv · FastAPI · Docker · VS Code
- Day 02 ✅ - Streaming /chat endpoint + Token cost calculator
- Day 03 ✅ - LCEL 3-step pipeline - rewrite/classify/respond with Pydantic schemas
- Day 04 ✅ - LlamaIndex QueryEngine + RouterQueryEngine + SubQuestionQueryEngine with Gemini
- Day 05 ✅ - Structured Output Engine — Invoice/Contract/Resume extraction with Gemini JSON mode 
- Day 06 ✅ - Built an autonomous tool-calling agent that detects intent and executes Google SerpAPI/  
               /Weather integration using the new GenAI SDK.
- Day 07 ✅ - Deployed the FastAPI streaming backend to Vercel with production security guards for   -              input-token
- Day 08 ✅ - Foundation for document Q&A systems — customer support bots, knowledge bases, policy search -              tools.
- Day 09 ✅ - Implemented hybrid search with BM25 + dense retrieval and RRF fusion
- Day 10 ✅ - Implemented HyDE retriever and benchmark vs naive RAG
- Day 11 ✅ - Built an automated RAGAS evaluation framework that scores RAG pipelines on faithfulness, -              answer relevancy, and context recall
- Day 12 ✅ - Implemented a contextual compression retriever with metadata filtering (85.7% reduction)
- Day 13 ✅ - Built a ReAct agentic RAG system combining retrieval, calculation, and live web search      -              tools, achieving 100% (15/15) correct tool selection
- Day 14 ✅ - Deployed production-grade Agentic RAG Assistant on Hugging Face Spaces with robust         -              dependency matching and LFS vector sync.
- Day 15 ✅ - Implemented and benchmarked three agent architectures (ReAct, Reflexion, Plan-and-Execute) -              on identical tasks; documented real failure modes — stale data selection, evaluator    -              miscalibration, and silent wrong answers from rigid planning.
- Day 16 ✅ - Day 16: Built a stateful multi-turn agent using LangGraph StateGraph + SqliteSaver —      -              persists full conversation history to SQLite restarts via thread_id session keys.
- Day 17 ✅ - 3-agent CrewAI pipeline (Researcher→Writer→Editor) with Ollama/llama3 locally — topic in, -              edited article out.
- Day 18 ✅ - Built LangGraph StateGraph with SqliteSaver persistent memory; key insight: LLM has no     -              memory, history is context fed each turn.
- Day 19 ✅ - Implemented agent guardrails: Guardrails AI, NeMo Guardrails (Colang DSL), infinite loop -              detection, tool error handling — adversarially tested.
- Day 20 ✅ - Built autonomous code-execution agent with LangChain ReAct + local exec() sandbox; -              write→execute→debug→fix loop working.
- Day 21 ✅ - ResearchPilot AI — LangGraph 4-node research agent (Groq Llama 3.3 70B + Gradio). GitHub:  -              ResearchPilotAI.
- Day 22 ✅ - Added LangSmith observability to ResearchPilot AI — full tracing, per-node latency, token/-              cost tracking, metadata tags, programmatic stats script.
- Day 23 ✅ - DSPy prompt optimization experiment — job-posting extraction task, hand-written baseline -              100% vs DSPy 91.67%, valid finding that DSPy's edge is on harder/larger-dataset tasks.
- Day 24 ✅ - Semantic caching layer using GPTCache + Redis Cloud  — cuts redundant LLM calls by catching -              paraphrased queries, delivering 94.4% cache hit rate and 75.3% latency reduction.
- Day 25 ✅ - Multi-modal extraction pipeline using Gemini 2.5 Flash Vision — classifies and extracts -              structured JSON from receipts, diagrams, and screenshots with 98%+ confidence.