import os
import requests
from dotenv import load_dotenv # Standard way to load keys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

# 1. SETUP
load_dotenv() # Loads keys from .env file
console = Console()

GROQ_KEY = os.getenv("GROQ_API_KEY")
WEATHER_KEY = os.getenv("WEATHER_API_KEY")

if not GROQ_KEY or not WEATHER_KEY:
    console.print("[bold red]❌ Error: Keys not found! Check your .env file.[/bold red]")
    exit()

llm = ChatGroq(api_key=GROQ_KEY, model="llama-3.1-8b-instant", temperature=0)

# 2. TOOLS
@tool
def get_current_weather_only(city: str) -> str:
    """Use ONLY for current/today's weather. NOT for future dates."""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_KEY}&q={city}"
    try:
        resp = requests.get(url).json()
        if "error" in resp: return f"Error: {resp['error']['message']}"
        return f"Weather Report: The current weather in {city} is {resp['current']['condition']['text']} with a temperature of {resp['current']['temp_c']}°C."
    except Exception as e: return f"Error: {e}"

@tool
def web_search(query: str) -> str:
    """Use for future weather, prices, or general info."""
    return DuckDuckGoSearchRun().run(query)

@tool
def budget_calculator(total_budget: str, days: str, people: str) -> str:
    """Calculates daily feasibility. Returns SIGNAL if budget is missing."""
    try:
        t = float(str(total_budget).replace(",", "").replace("$", "").replace("PKR", "").replace("RMB", ""))
        d = float(str(days))
        p = float(str(people))

        if t <= 10: 
            return "SIGNAL: Budget is unknown. Use 'web_search' to find prices."
        if d <= 0 or p <= 0:
            return "Error: Days/People must be > 0."

        daily = t / (d * p)
        status = "Tight" if daily < 5000 else "Comfortable"
        return f"Math Result: {daily:.2f} per person/day. Verdict: {status}."
    except:
        return "Error: Please provide numeric values."

tools = [get_current_weather_only, web_search, budget_calculator]

# 3. AGENT
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful Travel Assistant.
    CRITICAL INSTRUCTIONS:
    1. TRUST YOUR TOOLS: If 'get_current_weather_only' returns a report, repeat it exactly.
    2. BE DIRECT: Stop after you have the answer.
    3. FUTURE DATES: Use 'web_search'.
    4. BUDGET: Use 'budget_calculator'.
    """),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"), 
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=False, 
    return_intermediate_steps=True, max_iterations=2, early_stopping_method="force"
)

# 4. CLI LOOP
def start():
    console.print(Panel.fit("[bold cyan]🌍 Smart Travel Agent (CLI)[/bold cyan]", border_style="cyan"))
    chat_history = []
    
    while True:
        user_input = input("\n👉 ENTER YOUR QUERY HERE (or 'q' to quit): ")
        if user_input.lower() in ["q", "exit"]: 
            print("Safe travels!")
            break
        
        console.print(f"\n[bold yellow]--- Processing... ---[/bold yellow]")
        
        try:
            result = agent_executor.invoke({"input": user_input, "chat_history": chat_history})
            
            # Log Tools
            for step in result["intermediate_steps"]:
                console.print(Panel(
                    f"Tool: [cyan]{step[0].tool}[/cyan]\nResult: [dim]{str(step[1])[:200]}...[/dim]", 
                    title="[magenta]Tool Sequence[/magenta]", border_style="magenta"
                ))

            # Final Answer
            console.print(Panel(Markdown(result["output"]), title="[bold blue]Final Answer[/bold blue]", border_style="blue"))
            
            if len(chat_history) > 4: chat_history = chat_history[-2:]
            chat_history.extend([HumanMessage(content=user_input), AIMessage(content=result["output"])])

        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")

if __name__ == "__main__":
    start()