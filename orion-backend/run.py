# run.py
#!/usr/bin/env python3
"""
Orion Learning Agent Backend Runner - GEPA Powered
"""
import uvicorn
import os
from pathlib import Path


def main():
    """Run the GEPA-powered Orion Learning Agent backend"""
    print("🧠 Orion Learning Agent Backend - GEPA Powered")
    print("Self-Learning AI Agent with Advanced Tools")
    print("-" * 50)
    
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("   Please add OPENAI_API_KEY=your-key-here to your .env file")
        return
    
    # Ensure directories exist
    Path("example_threads").mkdir(exist_ok=True)
    Path("gepa_threads").mkdir(exist_ok=True)
    
    # Check for GEPA files (now in parent directory)
    print("🔍 Checking GEPA integration...")
    parent_dir = Path(__file__).parent.parent  # Go up to orion/
    
    gepa_files = {
        "amans_cli_orion.py": parent_dir / "amans_cli_orion.py",
        "gepa.py": parent_dir / "gepa.py"
    }
    
    missing_files = []
    found_files = []
    
    for name, file_path in gepa_files.items():
        if file_path.exists():
            found_files.append(name)
            print(f"✅ Found: {name}")
        else:
            missing_files.append(name)
            print(f"❌ Missing: {name}")
    
    # Check data directory
    data_dir = parent_dir / "data_lake"
    if data_dir.exists():
        print(f"✅ Data directory found: {data_dir}")
        json_files = list(data_dir.glob("*.json"))
        print(f"📊 Found {len(json_files)} JSON data files")
    else:
        print(f"❌ Data directory not found: {data_dir}")
    
    if missing_files:
        print(f"\n⚠️ Running in TESTING MODE")
        print(f"   Missing files: {', '.join(missing_files)}")
        print(f"   System will use mock tools for testing")
    else:
        print(f"✅ All GEPA files found - Full functionality available")
    
    print("\n🚀 Starting server...")
    
    # Run the FastAPI server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
