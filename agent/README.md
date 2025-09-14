.ve# Regulatory RAG Agent / סוכן רגולטורי חכם 🔍

A conversational AI-powered Retrieval-Augmented Generation (RAG) system for Israeli business regulatory compliance. This standalone agent provides Hebrew regulatory guidance through natural conversation, powered by OpenAI GPT-4o-mini and advanced vector search.

## 🌟 Features

### 🤖 Conversational AI Interface
- **Natural Hebrew conversation** - Collect business information through conversational flow
- **Smart information extraction** - Automatically extract business details from Hebrew text
- **Real-time guidance** - Immediate regulatory advice based on business profile

### 🎯 Advanced RAG System
- **Hybrid Search** - Combines semantic similarity with business compliance relevance
- **Hebrew Text Processing** - Full Hebrew language support with RTL interface
- **Intelligent Matching** - Context-aware regulation filtering based on business characteristics

### 🏢 Business Profiling
- **Conversational Profiling** - Extract business information through natural dialogue
- **Multi-attribute Support** - Seating capacity, size, business type, features
- **Compliance Filtering** - Show only relevant regulations for specific business

### 📊 Comprehensive Reporting
- **AI-Generated Reports** - Professional Hebrew compliance reports
- **Personalized Guidance** - Tailored recommendations based on business profile
- **Regulatory Summaries** - Clear explanations of complex requirements

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone and navigate to agent directory:**
```bash
cd agent
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set OpenAI API key:**
```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

4. **Run the application:**
```bash
python gradio_app.py
```

5. **Access the interface:**
Open `http://localhost:7860` in your browser

## 🏗️ System Architecture

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gradio UI     │───▶│   RAG System     │───▶│   OpenAI API    │
│  (Hebrew RTL)   │    │ (FAISS + Search) │    │  (GPT-4o-mini)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│Business Profiler│    │  Data Processor  │    │   Generator     │
│(Info Extraction)│    │ (JSON → Chunks)  │    │(Report Builder) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### File Structure

```
agent/
├── gradio_app.py          # Main Gradio web interface
├── rag_system.py          # Vector search and retrieval system
├── business_profiler.py   # Conversational business info extraction
├── generator.py           # AI report generation
├── data_processor.py      # JSON data processing and chunking
├── data.json             # Structured regulatory data
├── requirements.txt      # Python dependencies
├── basic_test.py         # Basic validation tests
├── test_rag_system.py    # Comprehensive system tests
└── conversational_demo.py # Command-line demo
```

## 📁 Component Details

### 🎪 Gradio Interface (`gradio_app.py`)
**Main web application with Hebrew RTL support**

**Key Features:**
- Conversational chat interface in Hebrew
- Real-time business profile collection
- Interactive compliance report generation
- System statistics and data upload
- Custom CSS for Hebrew RTL layout

**Usage:**
```python
from gradio_app import create_gradio_interface
demo = create_gradio_interface()
demo.launch()
```

### 🔍 RAG System (`rag_system.py`)
**Advanced retrieval system with FAISS vector search**

**Key Features:**
- Multilingual embeddings (`paraphrase-multilingual-mpnet-base-v2`)
- Hybrid search (semantic + compliance relevance)
- Business profile-aware filtering
- FAISS index persistence

**Example:**
```python
from rag_system import RegulatoryRAGSystem

rag = RegulatoryRAGSystem()
rag.build_index("data.json")

results = rag.hybrid_search(
    query="דרישות בטיחות אש למסעדה",
    business_profile={"seating_capacity": 80, "size_sqm": 120},
    k=5
)
```

### 👤 Business Profiler (`business_profiler.py`)
**Conversational business information extraction**

**Capabilities:**
- Hebrew text pattern matching
- Business type classification
- Numerical information extraction
- Conversation flow management

**Example:**
```python
from business_profiler import BusinessProfiler

profiler = BusinessProfiler()
profiler.update_business_info("אני מפעיל מסעדה עם 50 מקומות ישיבה")
profile = profiler.get_business_profile_dict()
```

### 🤖 Generator (`generator.py`)
**AI-powered Hebrew report generation**

**Features:**
- OpenAI GPT-4o-mini integration
- Hebrew regulatory system prompts
- Personalized compliance reports
- Context-aware response generation

**Example:**
```python
from generator import RegulatoryGenerator

generator = RegulatoryGenerator()
response = generator.generate_response(
    query="איזה דרישות בטיחות חלות עליי?",
    retrieved_chunks=search_results,
    business_profile=business_data
)
```

### 📊 Data Processor (`data_processor.py`)
**Regulatory data processing and chunking**

**Functionality:**
- JSON regulation parsing
- Business compliance checking
- Condition evaluation logic
- Searchable chunk creation

**Example:**
```python
from data_processor import RegulatoryDataProcessor

processor = RegulatoryDataProcessor("data.json")
processor.load_data()
chunks = processor.create_chunks()
applicable = processor.get_applicable_regulations(business_profile)
```

## 📋 Data Format

### Regulatory Data Structure (`data.json`)
```json
{
  "id": "FIRE_REQ_001",
  "requirement_name": "דרישות לעסקים קטנים במסלול תצהיר",
  "source_authority": "הרשות הארצית לכבאות והצלה",
  "category": "בטיחות אש",
  "conditions": [
    {
      "attribute": "seating_capacity",
      "operator": "less_than_or_equal_to",
      "value": 50
    }
  ],
  "raw_text": "בית אוכל... המיועד ל-50 איש לכל היותר...",
  "doc_source": "פרק 5"
}
```

### Business Profile Format
```python
{
    "seating_capacity": 80,
    "size_sqm": 120,
    "business_type": "מסעדה",
    "floors": 2,
    "has_kitchen": True,
    "has_storage": True,
    "has_outdoor_seating": False
}
```

## 🧪 Testing

### Basic System Validation
```bash
python basic_test.py
```
Tests:
- ✅ JSON data structure validation
- ✅ Data processor functionality  
- ✅ Code syntax validation
- ✅ Gradio interface structure
- ✅ Requirements file validation

### Comprehensive RAG Testing
```bash
python test_rag_system.py
```
Tests:
- ✅ Data processing pipeline
- ✅ FAISS index building and loading
- ✅ Hebrew semantic search
- ✅ Hybrid search algorithms
- ✅ AI report generation (requires API key)
- ✅ Full system integration

### Conversational Demo
```bash
python conversational_demo.py
```
- Interactive simulation of conversation flow
- Business profiling demonstration
- Hebrew information extraction testing

## 🎯 Usage Examples

### 1. Quick Start Demo
```python
# Run basic system validation
python basic_test.py

# Launch web interface
python gradio_app.py
# Visit http://localhost:7860
```

### 2. Command Line Demo
```python
# Test conversational flow
python conversational_demo.py

# Test full RAG system
python test_rag_system.py
```

### 3. Programmatic Usage
```python
from rag_system import RegulatoryRAGSystem
from generator import RegulatoryGenerator
from business_profiler import BusinessProfiler

# Initialize components
rag = RegulatoryRAGSystem()
rag.build_index("data.json")
generator = RegulatoryGenerator()
profiler = BusinessProfiler()

# Extract business info from Hebrew text
profiler.update_business_info("מסעדה עם 75 מקומות ישיבה")
business_profile = profiler.get_business_profile_dict()

# Search for relevant regulations
results = rag.hybrid_search(
    "דרישות בטיחות אש", 
    business_profile, 
    k=3
)

# Generate AI-powered response
response = generator.generate_response(
    "מה הדרישות שחלות על העסק שלי?",
    results,
    business_profile
)

print(response)
```

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here  # Required for AI generation
```

### Model Configuration
```python
# In rag_system.py
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# In generator.py  
LLM_MODEL = "gpt-4o-mini"
```

## 📦 Dependencies

**Core Libraries:**
- `gradio>=4.0.0` - Web interface
- `openai>=1.0.0` - AI integration
- `sentence-transformers>=2.2.0` - Embeddings
- `faiss-cpu>=1.7.0` - Vector search
- `numpy>=1.21.0` - Numerical computing

**Additional:**
- `torch>=1.12.0` - Deep learning backend
- `transformers>=4.21.0` - NLP models
- `pandas>=1.5.0` - Data processing
- `scikit-learn>=1.1.0` - ML utilities

See `requirements.txt` for complete list.

## 🌐 Deployment

### Local Development
```bash
python gradio_app.py
# Access: http://localhost:7860
```

### Gradio Spaces (Cloud)
1. Upload entire `agent/` directory to Gradio Spaces
2. Set `OPENAI_API_KEY` in Spaces secrets
3. Ensure `requirements.txt` is present
4. App will auto-launch at `app_file="gradio_app.py"`

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "gradio_app.py"]
```

## 🔍 Troubleshooting

### Common Issues

**1. OpenAI API Key Missing**
```
Warning: OPENAI_API_KEY not found in environment variables
```
**Solution:** Set your OpenAI API key as an environment variable

**2. FAISS Installation Issues**
```
ModuleNotFoundError: No module named 'faiss'
```
**Solution:** Install FAISS CPU version:
```bash
pip install faiss-cpu
```

**3. Hebrew Text Display Issues**
```
Hebrew text appears as boxes or question marks
```
**Solution:** Ensure browser supports Hebrew fonts and RTL text direction

**4. Model Download Timeout**
```
Connection timeout when downloading sentence-transformers model
```
**Solution:** Ensure stable internet connection or use local model cache

### Performance Optimization

**Index Building Speed:**
- Use SSD storage for faster file I/O
- Increase available RAM for large datasets
- Consider GPU acceleration for embeddings

**Search Performance:**
- Adjust `k` parameter for fewer results
- Use category filtering to reduce search space
- Cache frequently accessed business profiles

## 📈 System Statistics

**Regulatory Data:**
- 📊 9 fire safety regulations
- 🏢 Restaurant/food service focus
- 🇮🇱 Israeli regulatory framework
- 📋 Structured conditions and requirements

**AI Capabilities:**
- 🤖 GPT-4o-mini powered responses
- 🇮🇱 Native Hebrew language support
- 📝 Conversational information gathering
- 📊 Personalized compliance reports

**Technical Performance:**
- ⚡ Sub-second semantic search
- 🔍 Hybrid relevance scoring
- 💾 Persistent FAISS indexing
- 🌐 Web-ready Gradio interface

## 🤝 Contributing

This system is part of the larger **Regu-Biz / רגו-ביז** project. The agent component can be extended with:

1. **Additional Regulatory Data** - Expand beyond fire safety regulations
2. **Enhanced Business Types** - Support more business categories
3. **Advanced AI Features** - Multi-turn conversations, planning assistance
4. **Integration APIs** - Connect with external regulatory databases

## 📄 License

This project is part of an academic assignment for the **AImpact Hackathon**. See the main project repository for licensing information.

## 🙏 Acknowledgments

- **OpenAI** - GPT-4o-mini language model
- **Sentence Transformers** - Multilingual embedding models
- **FAISS** - Efficient similarity search
- **Gradio** - Rapid web interface development
- **Israeli Fire and Rescue Authority** - Regulatory data source

---

**רגו-ביז / Regu-Biz** - Making regulatory compliance accessible through AI 🚀
