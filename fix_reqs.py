import codecs

def fix_requirements():
    try:
        with codecs.open('requirements.txt', 'r', 'utf-16le') as f:
            content = f.read()
            
        print("Successfully read UTF-16LE requirements.txt")
        
        # Check for gunicorn and whitenoise
        lines = content.split('\n')
        has_gunicorn = any('gunicorn' in line.lower() for line in lines)
        has_whitenoise = any('whitenoise' in line.lower() for line in lines)
        
        if not has_gunicorn:
            content += '\ngunicorn>=21.2.0'
            print("Added gunicorn to requirements.txt")
        if not has_whitenoise:
            content += '\nwhitenoise>=6.6.0'
            print("Added whitenoise to requirements.txt")
            
        with codecs.open('requirements.txt', 'w', 'utf-8') as f:
            f.write(content)
            
        print("Successfully converted requirements.txt to UTF-8.")
        
    except Exception as e:
        print(f"Error: {e}")
        # Try to just append if it's already utf-8
        try:
            with codecs.open('requirements.txt', 'r', 'utf-8') as f:
                content = f.read()
            
            if 'gunicorn' not in content.lower():
                with codecs.open('requirements.txt', 'a', 'utf-8') as f:
                    f.write('\ngunicorn>=21.2.0\n')
            
            print("File is already UTF-8. Made sure gunicorn is present.")
        except Exception as e2:
            print(f"Second error: {e2}")

if __name__ == '__main__':
    fix_requirements()
