import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    import config
    print("Loaded config.py successfully")
    print(f"HF_API_TOKEN: {getattr(config, 'HF_API_TOKEN', 'Not Found')}")
    # Mask key for security in logs, show first/last few chars
    key = getattr(config, 'TONGYI_API_KEY', None)
    if key:
        print(f"TONGYI_API_KEY: {key[:6]}...{key[-4:]}")
    else:
        print("TONGYI_API_KEY: None")
        
    print(f"TONGYI_MODEL: {getattr(config, 'TONGYI_MODEL', 'Not Found')}")
    print(f"API_PRIORITY: {getattr(config, 'API_PRIORITY', 'Not Found')}")
except ImportError:
    print("Could not import config.py")

print("\nInitializing VOCAnalyzer...")
try:
    from voc_analyzer import VOCAnalyzer
    analyzer = VOCAnalyzer()
    print(f"Analyzer initialized.")
    print(f"Analyzer tongyi_model: {analyzer.tongyi_model}")
    print(f"Analyzer tongyi_key set: {bool(analyzer.tongyi_key)}")
    
    print("\nTesting analyze_with_ai...")
    result = analyzer.analyze_with_ai("这个软件太卡了，根本没法用")
    print(f"Analysis Result: {result}")
    
except Exception as e:
    print(f"Error initializing or running analyzer: {e}")
    import traceback
    traceback.print_exc()
