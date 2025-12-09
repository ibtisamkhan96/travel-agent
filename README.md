# 🌍 Smart Travel AI Agent

A CLI-based intelligent agent that plans trips using **LangChain** and **Llama 3**.
It features intelligent tool routing (Weather vs Search vs Math) and conversation memory.

## ✨ Features
* **Real-time Weather:** Uses WeatherAPI for current forecasts.
* **Budget Planning:** Calculates daily costs and warns if the budget is tight.
* **Smart Search:** Searches for flight/hotel prices if data is missing.
* **Memory:** Remembers context (e.g., budget details) across conversation turns.

## 🛠️ Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd travel-agent
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Keys**
    Create a file named `.env` in the root folder and add your keys:
    ```ini
    GROQ_API_KEY=your_key_here
    WEATHER_API_KEY=your_key_here
    ```

## 🚀 Usage
Run the main script:
```bash
python main.py
