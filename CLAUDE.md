# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is the **regu-biz / רגו-ביז** project - a business licensing assessment system for Israeli businesses. The core requirement is to build an end-to-end system that helps business owners understand regulatory requirements through AI-generated reports.

### Key Requirements from `משימה.md`
- Process business licensing data from provided PDF/Word documents
- Create digital questionnaire collecting business size, capacity, and special features
- **Critical**: AI integration using LLM (OpenAI/Claude/Gemini) to generate personalized compliance reports
- Convert legal language to clear business guidance
- Full working system required by September 14, 23:59

### Architecture Specifications
- **Frontend**: Simple UI (HTML/CSS/JS or React/Vue) with questionnaire and report display
- **Backend**: API server (Node.js/Python/Java) with data processing
- **AI Integration**: Primary component using LLM API for smart report generation
- **Data**: Structured storage for processed licensing requirements

## Development Approach

### Mandatory AI-First Development
Per project requirements, must use and document AI development tools:
- Recommended: Cursor AI, Windsurf, Replit, GitHub Copilot
- Document all AI tools used, LLM model selection, and prompts employed
- AI integration is the core differentiator, not an add-on

### Cursor Memory Bank Integration
This project uses Cursor's memory bank system (`.cursor/rules/memory-bank.mdc`) which maintains:
- Project brief and context across sessions
- Technical decisions and implementation patterns  
- Development progress tracking
- Must be consulted and updated as development progresses

## Current State

**Repository Status**: Complete functional system
- Full working React TypeScript frontend with Hebrew RTL support
- Python FastAPI backend with OpenAI GPT-5-mini integration
- End-to-end AI-powered regulatory report generation
- Ready for final submission preparation

## Expected Deliverables

### Technical Implementation
- Complete Git repository with meaningful commit history
- Functional API with documented endpoints
- Working frontend with questionnaire interface
- Active AI integration producing real regulatory reports
- Data processing pipeline for licensing documents

### Documentation Requirements
- Installation and runtime instructions
- API endpoint documentation
- System architecture overview
- AI integration details (model choice, prompt engineering)
- Development journal documenting challenges and solutions

## Key Constraints

- **Timeline**: Extremely tight deadline requires rapid prototyping approach
- **Focus**: Functionality over polish - working system more important than UI/UX
- **Language**: Some content in Hebrew, ensure proper encoding and display
- **AI Dependency**: System effectiveness relies heavily on quality of LLM integration

This repository requires full initial development - architecture decisions, technology selection, and complete implementation from scratch.

## Memory Bank System

Claude Code operates with session context that can benefit from a structured memory bank approach. This system ensures continuity and effective collaboration across development sessions.

### Memory Bank Structure

The Memory Bank consists of core files that build upon each other in a clear hierarchy:

```
memory-bank/
├── projectbrief.md      # Foundation document - core requirements and goals
├── productContext.md    # Why this project exists, problems it solves
├── activeContext.md     # Current work focus, recent changes, next steps
├── systemPatterns.md    # System architecture, key technical decisions
├── techContext.md       # Technologies used, development setup, constraints
└── progress.md          # What works, what's left to build, current status
```

### Core Files (Required)

1. **projectbrief.md** - Foundation document that shapes all other files
2. **productContext.md** - Why this project exists and how it should work
3. **activeContext.md** - Current work focus and recent changes
4. **systemPatterns.md** - System architecture and design patterns
5. **techContext.md** - Technologies used and development setup
6. **progress.md** - Current status and what works

### Documentation Updates
Memory Bank updates should occur when:
- Discovering new project patterns
- After implementing significant changes
- When context needs clarification for future sessions
- When user requests **update memory bank**

### Project Intelligence Integration
This system ensures that each Claude Code session can quickly understand project context and continue work effectively.