# AMD-Developer-Hackathon

# Hardware-Aware Code Optimization Agent
An agentic system that recursively analyzes performance-critical Python code
and suggests hardware-aware optimizations for AMD platforms.

## What it does
- Recursively decomposes a codebase into functions and loops (RLM pattern)
- Pre-flags hardware hints: nested loops, cache-unfriendly access, redundant computation
- Uses an LLM to generate optimization suggestions
- Produces a structured markdown report with severity rankings

## Architecture
Input code → Planner → RLM Loop → Analyzer (LLM) → Reporter → Markdown report
↕
state.json (environment)

## Quick Start

## Tech Stack
- **Agent framework:** CrewAI
- **LLM:** 
- **Code parsing:** Python `ast` module
- **State storage:** JSON
- **Output:** Markdown

