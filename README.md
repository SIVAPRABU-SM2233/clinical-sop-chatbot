# Clinical SOP Chatbot

A portfolio project that demonstrates how to build a conversational AI application for working with clinical standard operating procedures (SOPs). The project focuses on practical LLM application patterns: model integration, conversation memory, token-aware context selection, persistence, and testable chat behavior.

This repository is intended to showcase software engineering and AI application skills for hiring managers and technical collaborators.

## Why this project

This project was built to explore the core building blocks of a real-world chatbot:

- Connecting a Python app to an LLM API
- Managing conversation history across turns
- Controlling context size using token estimates
- Handling oversized messages gracefully
- Persisting chat state locally
- Testing model interactions without relying on live API calls
- Designing for future compaction and memory features

It shows how a chatbot evolves from a simple prompt-response app into a more robust application with context management and production-minded thinking.

## What this project demonstrates

- Python application architecture for an LLM chat loop
- OpenAI API integration using the official Python SDK
- Message history handling for multi-turn conversations
- Local JSON persistence for chat state
- Token-aware context selection to keep prompts within a budget
- Validation for oversized user inputs
- Mock-based testing for deterministic, cost-safe verification
- Separation of concerns between chat loop logic, response generation, and state storage

## Project highlights

- Built with Python
- Uses OpenAI Responses API via the OpenAI SDK
- Uses tiktoken to estimate token usage locally
- Stores chat history in JSON for simple persistence
- Includes unit tests covering chat behavior and context selection
- Designed to be extended with summarization, RAG, and tool use

## Typical use case

The app is structured as a foundation for an SOP assistant that can help with procedural questions in a clinical context. While this version is a learning and showcase project rather than a regulated clinical product, it demonstrates the engineering patterns required for building production-facing AI assistants.

## Tech stack

- Python 3.10+
- OpenAI Python SDK
- tiktoken
- JSON for persistence
- unittest for automated tests

## Setup

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies
4. Set your OpenAI API key in the environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install openai tiktoken
```

On Windows PowerShell:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install openai tiktoken
```

Set the API key:

```bash
export OPENAI_API_KEY="your-api-key"
```

On Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your-api-key"
```

## Run the app

```bash
python main.py
```

The app will prompt for a message and keep a conversation history in a local JSON file while the program runs.

## Run tests

```bash
python -m unittest -v
```

The test suite checks chat-loop behavior and model interaction patterns while avoiding live API calls through mocked responses.

## Repository structure

- main.py — chatbot loop and context logic
- test_main.py — automated tests
- .gitignore — excludes local runtime and sensitive files
- persistence_test_history.json — local chat state storage

## Design considerations

This project focuses on practical engineering decisions that are relevant in real AI products:

- Conversation history must be managed carefully to stay within model limits
- Token budget logic is more useful than a fixed message count
- Prompt size matters because it directly impacts latency and cost
- Persistence and summarization are important for long-running conversations
- Testability matters because live model calls are slow, expensive, and inconsistent

## Future improvements

Possible next steps for this project include:

- Summarization and compaction for long conversations
- Retrieval-augmented generation for SOP documents
- Better structured outputs for clinical workflows
- Logging and telemetry
- A web interface or API wrapper
- Safer handling of sensitive clinical text and user data

## Notes

This project is a demonstration of AI and Python engineering skills rather than a production clinical decision support system. It is structured to show thoughtful implementation, clean separation of logic, and awareness of the real constraints of AI-powered applications.

## License

This project is for learning and portfolio purposes.
