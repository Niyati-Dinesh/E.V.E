# E.V.E. System 🤖

> **Work in Progress** - AI-powered multi-worker system with distributed task processing

## Overview

E.V.E. (Evolutionary Virtual Engine) is a master-worker architecture system that coordinates multiple AI workers for different tasks including code generation, documentation, and analysis.

## Architecture

- **Master Controller** - Central coordination hub (Port 8000)
- **Coding Worker** - Code generation and modification (Port 5001)
- **Documentation Worker** - Documentation generation with PDF/DOCX support (Port 5002)
- **Analysis Worker** - Code analysis and review (Port 5003)

## Prerequisites

- Python 3.8+
- PostgreSQL database
- GROQ API key ([Get one here](https://console.groq.com))

## Project Status

🚧 **Currently in Development**

- [x] Master controller setup
- [x] Multi-worker coordination
- [x] Basic task routing
- [ ] Advanced error handling
- [ ] Performance optimization
- [ ] Comprehensive testing

## Technologies

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL
- **AI/LLM**: GROQ API, Ollama Cloud (Gemma3, Qwen3)
- **Architecture**: Microservices, Master-Worker Pattern
- **Frontend**: Reactjs , Tailwindcss

## Contributing

This is a personal project currently under active development.


---

**Note**: This system is part of an ongoing research/development project. Features and architecture may change.
