# ULTRON AI - Technology Stack

**Version:** 1.0

---

# Philosophy

Technology should be selected based on the following priorities:

1. Local-first execution
2. Performance
3. Stability
4. Long-term maintainability
5. Open-source ecosystem
6. Cross-platform compatibility
7. Modularity

The objective is to minimize unnecessary dependencies while ensuring every technology has a clear purpose.

---

# System Overview

| Layer              | Technology                   |
| ------------------ | ---------------------------- |
| Frontend           | Next.js + React + TypeScript |
| Backend            | Python + FastAPI             |
| AI Runtime         | Ollama                       |
| Agent Framework    | LangGraph                    |
| Database           | SQLite                       |
| Vector Database    | ChromaDB                     |
| Voice STT          | Whisper.cpp                  |
| Voice TTS          | Piper TTS                    |
| Wake Word          | OpenWakeWord                 |
| Browser Automation | Playwright                   |
| macOS Automation   | AppleScript + Python         |
| Desktop App        | Tauri (Future)               |
| 3D Graphics        | Three.js                     |
| State Management   | Zustand                      |
| API Communication  | REST + WebSockets            |
| Authentication     | Local User Profiles (Future) |

---

# Frontend

## Next.js

Purpose:

* Dashboard
* Chat UI
* Orb Interface
* Widgets
* Settings
* Future Web Dashboard

Why:

* Modern architecture
* Excellent performance
* React ecosystem
* TypeScript support
* Long-term maintainability

---

## React

Purpose:

* Component-based UI
* Dynamic rendering
* State-driven interface

---

## TypeScript

Purpose:

* Type safety
* Better IDE support
* Reduced runtime errors
* Easier scaling

Mandatory throughout the frontend.

---

## Tailwind CSS

Purpose:

* Utility-first styling
* Dark futuristic UI
* Rapid development
* Consistent design system

---

## Three.js

Purpose:

* Animated Orb
* Particle systems
* Dashboard effects
* Holographic UI
* 3D visualizations

---

# Backend

## Python

Purpose:

Primary backend language.

Why:

* Best AI ecosystem
* Excellent automation support
* Cross-platform
* Huge community

---

## FastAPI

Purpose:

Backend API server.

Responsibilities:

* REST API
* WebSockets
* Agent communication
* Tool execution
* Authentication
* Session management

---

# AI Runtime

## Ollama

Purpose:

Run all LLMs locally.

Benefits:

* Offline inference
* Easy model management
* REST API
* Cross-platform
* Active development

---

# Language Models

## General Assistant

Recommended:

* Qwen 3 8B Instruct (or another capable local 8B instruct model)

Purpose:

* Conversation
* Planning
* Reasoning
* Tool selection
* General knowledge

---

## Coding Assistant

Current model:

* Qwen2.5-Coder 14B

Purpose:

* Code generation
* Refactoring
* Debugging
* Documentation
* Testing
* Project creation

---

## Vision Model (Future)

Purpose:

* Image understanding
* OCR
* UI recognition
* Screenshot analysis
* Camera input

---

# Agent Framework

## LangGraph

Purpose:

Coordinate:

* Planner
* Memory
* Agents
* Tools
* Long-running workflows

Chosen because it supports stateful, multi-step agent execution better than simple prompt chaining.

---

# Memory

## SQLite

Stores:

* Conversations
* Settings
* Tasks
* Notes
* User Profile
* Projects

Advantages:

* Local
* Reliable
* Lightweight
* No server required

---

## ChromaDB

Purpose:

Semantic memory.

Stores:

* Embeddings
* Knowledge
* Long-term memories

Supports retrieval-augmented generation (RAG).

---

# Voice

## Whisper.cpp

Purpose:

Speech-to-text.

Advantages:

* Local
* Fast
* Offline
* Accurate

---

## Piper TTS

Purpose:

Text-to-speech.

Advantages:

* Local
* Lightweight
* Fast
* Natural voice quality

---

## OpenWakeWord

Purpose:

Wake-word detection.

Example:

"Hey ULTRON"

Designed to consume very little CPU while always listening.

---

# Browser Automation

## Playwright

Purpose:

* Open websites
* Login
* Fill forms
* Search
* Download files
* Upload files
* Automation workflows

Chosen because it is more reliable than Selenium for modern browsers.

---

# macOS Automation

Primary technologies:

* AppleScript
* Python subprocess
* Native shell commands

Capabilities:

* Open apps
* Finder operations
* Notifications
* Terminal automation
* Media control

---

# Desktop Application

## Tauri (Future)

Purpose:

Wrap the web interface as a native desktop application.

Advantages:

* Lower memory usage than Electron
* Faster startup
* Better integration with the operating system

---

# State Management

## Zustand

Purpose:

Manage frontend application state.

Chosen for simplicity and performance.

---

# Networking

REST API

Used for:

* Commands
* Configuration
* Data retrieval

WebSockets

Used for:

* Live chat
* Streaming responses
* System monitoring
* Notifications
* Voice events

---

# Logging

Python logging

Stores:

* Errors
* Tool execution
* Agent decisions
* Performance metrics

Sensitive information should never be written to logs.

---

# Testing

Frontend:

* Vitest
* React Testing Library

Backend:

* Pytest

Automation:

* Playwright Tests

---

# Development Tools

Python

* uv (preferred) or pip
* Ruff
* Black
* MyPy

JavaScript

* npm or pnpm
* ESLint
* Prettier

Git

* GitHub
* Conventional Commits
* GitHub Actions (Future)

---

# Hardware Compatibility

Primary development machine:

MacBook Pro 2019

Specifications:

* Intel Core i7
* 32 GB RAM
* 512 GB SSD
* AMD Radeon Pro 4 GB

Target idle resource usage:

* RAM: under 3 GB (without model loaded)
* CPU: under 10% when idle
* FastAPI startup: under 5 seconds
* Dashboard: smooth at 60 FPS
* Voice response latency: under 2 seconds (model dependent)

---

# Future Technologies

Potential additions:

* OpenCV
* ONNX Runtime
* llama.cpp
* Redis (optional)
* PostgreSQL (optional)
* Home Assistant
* ROS2
* MQTT
* Docker
* Kubernetes (remote deployments)

---

# Dependency Policy

Before adding a new dependency, verify:

* Is it actively maintained?
* Is it open source?
* Does it improve the architecture?
* Can an existing dependency already solve the problem?
* Is it lightweight?
* Does it support macOS?

If the answer to most of these is "no", avoid adding it.

---

# Guiding Principle

ULTRON should remain a lightweight, modular, local-first AI operating system. Every technology in the stack must contribute directly to performance, maintainability, extensibility, or user experience. Complexity should only be introduced when it provides measurable value.
