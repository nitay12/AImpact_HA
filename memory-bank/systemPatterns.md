# System Patterns: Architecture and Design Decisions

## Overall Architecture - IMPLEMENTED SYSTEM

### High-Level System Design (COMPLETED)
```
[React Frontend (Vite + TypeScript)]
       ↓ HTTP/CORS
[FastAPI Backend (Python)]
       ↓
[Regulatory Data Processing] ← [OpenAI GPT-5-mini Integration]
       ↓
[JSON Data Store + Memory]
```

### Implemented Component Architecture
- **Frontend**: React TypeScript app with Hebrew RTL support, questionnaire forms, and report display
- **Backend API**: FastAPI server with automatic documentation, CORS support, and comprehensive error handling
- **Data Processor**: PyMuPDF-based extractor converting Hebrew regulatory documents to structured JSON
- **AI Engine**: OpenAI GPT-5-mini integration with specialized Hebrew regulatory prompts
- **Data Store**: JSON-based structured storage with requirement matching and business rules engine

## Core Design Patterns

### 1. Data Processing Pipeline
```
Raw Documents (PDF/Word) 
    → Document Parser 
    → Data Extractor 
    → Structure Mapper 
    → Validation Layer 
    → Structured Data Store
```

**Pattern**: ETL (Extract, Transform, Load)
- **Extract**: Parse source documents for relevant content
- **Transform**: Structure data into queryable format
- **Load**: Store in consistent schema for API consumption

### 2. Business Logic Matching
```
User Input 
    → Business Profile Builder 
    → Requirement Matcher 
    → Relevance Scorer 
    → Filtered Requirements
```

**Pattern**: Rule-Based Filtering with Scoring
- Business characteristics mapped to requirement criteria
- Multi-dimensional matching (size, type, features)
- Relevance scoring for prioritization

### 3. AI Integration Pattern
```
Filtered Requirements 
    → Context Builder 
    → Prompt Generator 
    → LLM API Call 
    → Response Parser 
    → Report Formatter
```

**Pattern**: AI-Augmented Processing
- Structured data provides context to AI
- AI enhances with natural language generation
- Human-readable output from technical requirements

### 4. API Design Pattern (IMPLEMENTED)
**RESTful Resource-Oriented Design with FastAPI**
- `POST /api/generate-report` - Submit questionnaire and generate AI-powered Hebrew compliance report
- `POST /api/questionnaire/submit` - Submit questionnaire and get matched requirements
- `POST /api/match-requirements` - Direct requirement matching with BusinessProfile
- `GET /api/sample-profiles` - Get sample business profiles for testing
- `POST /api/sample-profiles/{profile_name}` - Test matching with sample profile
- `GET /api/health` - Health check endpoint
- `GET /api/stats` - Get statistics about loaded regulatory data
- `GET /api/ai/test-connection` - Test AI service connection

## Data Flow Patterns

### 1. Request-Response Flow
```
Frontend → API Gateway → Business Logic → Data Layer → AI Service → Response
```

### 2. Data Processing Flow
```
Source Documents → Parser → Validator → Transformer → Storage → API Access
```

### 3. Report Generation Flow
```
User Input → Requirement Matching → Context Preparation → AI Processing → Report Assembly
```

## Key Technical Decisions

### Data Storage Strategy
**Decision**: JSON-based file storage with optional database upgrade path
**Rationale**: 
- Simplicity for initial development
- Easy to inspect and debug
- Rapid prototyping without database setup
- Clear upgrade path to PostgreSQL/MongoDB if needed

### AI Integration Approach
**Decision**: External API integration (OpenAI/Claude/Gemini)
**Rationale**:
- Access to state-of-the-art language models
- No need for local model management
- Reliable, scalable service
- Focus on application logic rather than AI infrastructure

### Frontend Architecture
**Decision**: React-based SPA with API communication
**Rationale**:
- Modern, maintainable frontend stack
- Clear separation of concerns
- Good developer experience
- Easy to extend and modify

### Error Handling Pattern
**Decision**: Graceful degradation with fallback responses
**Rationale**:
- AI services can be unreliable
- System should work even with partial functionality
- Clear error messages for debugging and user experience

## Security Considerations

### API Security
- Input validation and sanitization
- Rate limiting for AI API calls
- Secure handling of API keys
- CORS configuration for frontend integration

### Data Privacy
- No persistent storage of personal business information
- Session-based data handling
- Clear data retention policies
- Anonymized logging

## Scalability Patterns

### Horizontal Scaling Readiness
- Stateless API design
- External data storage
- Configurable AI service endpoints
- Environment-based configuration

### Performance Optimization
- Caching strategies for processed regulatory data
- Async processing for AI report generation
- Connection pooling for external services
- Response compression

## Testing Strategy

### Testing Pyramid
- **Unit Tests**: Core business logic and data processing
- **Integration Tests**: API endpoints and AI integration
- **End-to-End Tests**: Complete user workflows
- **Manual Testing**: AI output quality and user experience

### AI Testing Approach
- Prompt engineering validation
- Output quality assessment
- Edge case handling
- Fallback behavior verification
