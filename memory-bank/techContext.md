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
**Primary Choice**: Node.js with Express
- **Node.js 18+**: JavaScript runtime for backend development
- **Express.js**: Minimal, flexible web application framework
- **TypeScript**: Consistent language across frontend and backend
- **Cors**: Cross-origin resource sharing middleware
- **Morgan**: HTTP request logger middleware
- **Helmet**: Security middleware

**Alternative Options**: Python with Flask, Java with Spring Boot

### AI Integration
**Primary Choice**: OpenAI API (GPT-4/GPT-3.5-turbo)
- **OpenAI SDK**: Official JavaScript/TypeScript client
- **Anthropic Claude**: Alternative LLM provider
- **Google Gemini**: Additional option for comparison

### Data Processing
**Technology Stack**:
- **PDF Parser**: pdf-parse or pdf2json for PDF document processing
- **Document Processing**: mammoth for Word document handling
- **Data Validation**: Joi or Zod for schema validation
- **JSON Storage**: Native JSON file handling with fs-extra

### Development Tools
**Required AI Tools** (as per assignment):
- **Cursor AI**: Primary development environment with AI assistance
- **GitHub Copilot**: Code completion and suggestion
- **ChatGPT/Claude**: Problem-solving and architecture discussions
- **Documentation**: AI-assisted README and documentation generation

## Development Environment

### Local Setup Requirements
```bash
# Node.js and npm
node --version  # v18.0.0 or higher
npm --version   # v8.0.0 or higher

# Git for version control
git --version

# Environment variables
API_KEY=your_openai_api_key
PORT=3000
NODE_ENV=development
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
├── backend/                 # Express.js API
│   ├── src/
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── models/          # Data models
│   │   ├── utils/           # Utilities
│   │   └── middleware/      # Express middleware
│   └── package.json
├── data/                    # Processed regulatory data
│   ├── raw/                 # Original PDF/Word files
│   ├── processed/           # Structured JSON data
│   └── scripts/             # Data processing scripts
├── docs/                    # Documentation
└── memory-bank/             # Memory bank files
```

### Dependencies

#### Backend Dependencies
```json
{
  "dependencies": {
    "express": "^4.18.0",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "morgan": "^1.10.0",
    "openai": "^4.0.0",
    "pdf-parse": "^1.1.1",
    "mammoth": "^1.6.0",
    "joi": "^17.9.0",
    "fs-extra": "^11.1.0",
    "dotenv": "^16.3.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/express": "^4.17.0",
    "typescript": "^5.0.0",
    "ts-node": "^10.9.0",
    "nodemon": "^3.0.0",
    "jest": "^29.0.0"
  }
}
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
