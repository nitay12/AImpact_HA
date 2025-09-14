#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regu-Biz / רגו-ביז - Main Application Entry Point
Business licensing assessment system for Israeli businesses.
"""

import uvicorn

# Import the app using absolute import that works with the current structure
import sys
from pathlib import Path

# Add the backend directory to the Python path so relative imports work
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from api.matching import app

def main():
    """Run the FastAPI server."""
    print("Starting Regu-Biz / רגו-ביז - Business Licensing API Server...")
    print("Documentation available at: http://localhost:8000/docs")
    print("Health check at: http://localhost:8000/health")
    
    uvicorn.run(
        "api.matching:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
