import sys
import subprocess

def fix_requirements():
    print("Restoring requirements.txt...")
    try:
        # 1. Install required packages for Render just in case
        print("Ensuring gunicorn and whitenoise are installed...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gunicorn>=21.2.0', 'whitenoise>=6.6.0'])
        
        # 2. Get pip freeze output
        print("Grabbing all installed packages...")
        reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode('utf-8', errors='ignore')
        
        # 3. Write it back to requirements.txt in proper UTF-8
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(reqs)
            
        print("\nSUCCESS: Your requirements.txt is restored and properly formatted as UTF-8!")
    except Exception as e:
        print(f"Failed to fix: {e}")

if __name__ == '__main__':
    fix_requirements()
