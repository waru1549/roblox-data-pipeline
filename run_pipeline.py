import subprocess
import sys
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
BASE_DIR = Path(__file__).resolve().parent

# ลำดับสคริปต์ที่ต้องรันใน Pipeline
PIPELINE_SCRIPTS = [
    "ingest.py",
    "transform.py",
    "publish.py"
]

def run_script(script_name):
    """ฟังก์ชันสำหรับเรียกใช้สคริปต์ Python แต่ละตัว"""
    print(f"\n{'='*50}")
    print(f" ▶️ RUNNING: {script_name}")
    print(f"{'='*50}")
    
    script_path = BASE_DIR / script_name
    
    if not script_path.exists():
        print(f"\n[ERROR] File not found: {script_path}")
        sys.exit(1)
        
    # ใช้ subprocess เพื่อรันสคริปต์เสมือนพิมพ์คำสั่งบน Terminal
    result = subprocess.run([sys.executable, str(script_path)])
    
    if result.returncode != 0:
        print(f"\n[ERROR] Pipeline stopped. Failed at {script_name}!")
        sys.exit(1)
        
    print(f"\n[SUCCESS] {script_name} completed.")

def main():
    print("==================================================")
    print(" 🚀 STARTING ROBLOX DATA AUTOMATED PIPELINE")
    print("==================================================")
    
    for script in PIPELINE_SCRIPTS:
        run_script(script)
        
    print("\n==================================================")
    print(" 🎉 PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    main()