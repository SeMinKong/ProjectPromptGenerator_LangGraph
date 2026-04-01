# Project Design Prompt Generator (LangGraph) 🚀

**[한국어 버전](./README.md)**

An advanced AI-driven design platform built with **LangGraph** and **Upstage Solar Pro**. This tool orchestrates a structured dialogue across multiple software design dimensions to automatically generate comprehensive, implementation-ready AI prompts for your next project.

## 🚀 Key Features

- **Parallel Graph Architecture**: Leverages **LangGraph** to manage 6+ design dimensions (UI/UX, Architecture, DB, API, etc.) simultaneously.
- **Multi-round Iterative Dialogue**: Each dimension conducts up to 3 rounds of specialized Q&A to refine project requirements.
- **Automated Prompt Engineering**: Translates conversation history into high-quality, structured prompts for LLMs (ChatGPT, Claude, etc.).
- **Real-time Synchronization**: Powered by **FastAPI** and **WebSockets** for live status updates and instant prompt previews.
- **Extensible Dimensions**: Easily add custom design perspectives (e.g., Security, DevOps) to fit specific project needs.

## 🛠 Tech Stack

- **AI Orchestration**: LangGraph, LangChain
- **LLM**: Upstage Solar Pro
- **Backend**: FastAPI, WebSocket
- **Frontend**: Vanilla JS, HTML5, CSS3
- **DevOps**: Docker

## 🏗 Project Structure

```text
├── server/             # FastAPI & WebSocket handlers
├── dimensions/         # LLM logic per design dimension
├── prompts/            # System prompts & round configurations
├── frontend/           # Interactive 3-panel web UI
└── state.py            # LangGraph state definitions
```

## 🧠 Technical Highlights

### 1. State-Machine Based Dialogue
Using LangGraph's state management, I implemented a robust "Turn-based" system where each design dimension tracks its own message history, current round, and completion status independently. This allows for complex, multi-agent-like behavior without the overhead of full agents.

### 2. Parallel Processing with WebSockets
To avoid long wait times, all design dimensions are initialized and processed in parallel. As the LLM generates questions or final prompts, the server pushes updates to the client via WebSockets, ensuring a highly responsive user experience.

## 🏁 Quick Start

### Prerequisites
- Python 3.11+
- [Upstage API Key](https://console.upstage.ai/)

### Installation & Run
```bash
git clone <repository-url>
cd ProjectPromptGenerator_LangGraph
pip install -r requirements.txt
echo "UPSTAGE_API_KEY=your_key_here" > .env
uvicorn server.app:app --reload
```
Open `http://localhost:8000` to start designing.

## 🎮 How to Use
1. **Enter Project Idea**: Describe what you want to build.
2. **Select Dimensions**: Choose the design areas you want to focus on.
3. **Engage in Dialogue**: Answer the AI's specialized questions in each tab.
4. **Export Result**: Copy the final integrated design document and feed it to your favorite LLM for implementation.

---
Built with ❤️ using LangGraph & Upstage Solar.
