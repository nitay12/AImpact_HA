# Technical Context: Technologies and Implementation

## Technology Stack

### Frontend
**Primary Choice**: React with TypeScript
- **React 18+**: Modern component-based UI framework
- **TypeScript**: Type safety and better developer experience
- **Axios**: HTTP client for API communication
- **React Router**: Single-page application navigation
- **CSS Modules/Styled-Components**: Component-scoped styling

**Alternative Options**: Vue.js, vanilla HTML/CSS/JS for simplicity

### Backend
**Primary Choice**: Python with FastAPI
- **Python 3.9+**: Modern Python runtime for backend development
- **FastAPI**: High-performance, easy-to-use web framework with automatic API documentation
- **Pydantic**: Data validation and serialization with type hints
- **Uvicorn**: Lightning-fast ASGI server
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping

**Alternative Options**: Node.js with Express, Java with Spring Boot

### AI Integration
**Primary Choice**: OpenAI API (GPT-4/GPT-3.5-turbo)
- **OpenAI Python SDK**: Official Python client
- **Anthropic Claude**: Alternative LLM provider with Python SDK
- **Google Gemini**: Additional option for comparison

### Data Processing
**Technology Stack**:
- **PDF Parser**: PyPDF2 or pdfplumber for PDF document processing
- **Document Processing**: python-docx for Word document handling
- **Data Validation**: Pydantic for schema validation and type safety
- **JSON Storage**: Native JSON handling with Python standard library

### Development Tools
**Required AI Tools** (as per assignment):
- **Cursor AI**: Primary development environment with AI assistance
- **GitHub Copilot**: Code completion and suggestion
- **ChatGPT/Claude**: Problem-solving and architecture discussions
- **Documentation**: AI-assisted README and documentation generation

## Development Environment

### Local Setup Requirements
```bash
# Python and pip
python --version  # v3.9.0 or higher
pip --version     # v21.0.0 or higher

# UV package manager (preferred)
uv --version

# Git for version control
git --version

# Environment variables
OPENAI_API_KEY=your_openai_api_key
PORT=8000
ENVIRONMENT=development
```

### Project Structure
```
AImpact_HA/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API communication
│   │   ├── types/           # TypeScript interfaces
│   │   └── utils/           # Helper functions
│   ├── public/              # Static assets
│   └── package.json
├── backend/                 # FastAPI Application
│   ├── app/
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── models/          # Pydantic data models
│   │   ├── utils/           # Utilities
│   │   └── dependencies/    # FastAPI dependencies
│   ├── models/              # Database models
│   └── requirements.txt
├── data/                    # Processed regulatory data
│   ├── raw/                 # Original PDF/Word files
│   ├── processed/           # Structured JSON data
│   └── scripts/             # Data processing scripts
├── docs/                    # Documentation
└── memory-bank/             # Memory bank files
```

### Dependencies

#### Backend Dependencies (requirements.txt)
```txt
# FastAPI and server
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Data validation and serialization
pydantic==2.5.0
pydantic-settings==2.1.0

# Database and ORM
sqlalchemy==2.0.23

# AI SDKs
openai==1.3.7
anthropic==0.7.7
google-generativeai==0.3.1

# Environment management
python-dotenv==1.0.0

# Document processing
pypdf2==3.0.1
python-docx==1.1.0

# Development dependencies
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
mypy==1.7.1
```
```

#### Frontend Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.4.0",
    "typescript": "^5.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^4.4.0"
  }
}
```

## Technical Constraints

### Performance Requirements
- **API Response Time**: < 2 seconds for standard requests
- **AI Report Generation**: < 30 seconds for complex reports
- **File Processing**: Handle PDF/Word files up to 10MB
- **Concurrent Users**: Support for 10+ simultaneous users

### Security Requirements
- **API Key Management**: Secure storage of external API keys
- **Input Validation**: All user inputs validated and sanitized
- **Rate Limiting**: Prevent abuse of AI API calls
- **Error Handling**: No sensitive information in error responses

### Compatibility Requirements
- **Browser Support**: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+)
- **Node.js Version**: 18.0.0 or higher
- **Operating System**: Cross-platform (Windows, macOS, Linux)

## AI Integration Specifications

### OpenAI API Configuration
```typescript
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  timeout: 30000,
  maxRetries: 3
});
```

### Prompt Engineering Strategy
- **System Prompts**: Define AI role and output format
- **Context Injection**: Provide structured data context
- **Output Formatting**: Request specific JSON/Markdown formats
- **Error Handling**: Graceful fallbacks for API failures

### AI Service Architecture
```typescript
interface AIService {
  generateReport(businessData: BusinessProfile, requirements: Requirement[]): Promise<Report>;
  summarizeRequirements(requirements: Requirement[]): Promise<Summary>;
  translateToBusinessLanguage(legalText: string): Promise<string>;
}
```

## Data Schemas

### Business Profile Schema
```typescript
interface BusinessProfile {
  size: number;           // Size in square meters
  seatingCapacity: number; // Number of seats
  hasGasUsage: boolean;   // Uses gas equipment
  servesAlcohol: boolean; // Serves alcoholic beverages
  hasDelivery: boolean;   // Offers delivery service
  businessType: 'restaurant' | 'cafe' | 'fast_food' | 'catering';
}
```

### Requirement Schema
```typescript
interface Requirement {
  id: string;
  title: string;
  description: string;
  category: string;
  applicabilityRules: ApplicabilityRule[];
  priority: 'high' | 'medium' | 'low';
  deadline?: string;
  authority: string;
  contactInfo?: ContactInfo;
}
```

## Development Workflow

### Git Workflow
- **Main Branch**: Production-ready code
- **Feature Branches**: Individual feature development
- **Commit Messages**: Conventional commit format
- **AI Tool Documentation**: Include AI assistance in commit messages

### Testing Strategy
- **Unit Tests**: Jest for backend logic testing
- **Integration Tests**: API endpoint testing
- **Manual Testing**: AI output quality assessment
- **Documentation Testing**: README instruction validation

### Deployment Preparation
- **Environment Configuration**: Development, staging, production configs
- **Build Process**: Automated frontend build and backend compilation
- **Docker Support**: Optional containerization for deployment
- **Environment Variables**: Secure handling of API keys and configuration
