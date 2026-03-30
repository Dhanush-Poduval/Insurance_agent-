import os

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = content.replace('from db_models import', 'from db_models import')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✓ Fixed {filepath}")
            except Exception as e:
                print(f"✗ Error in {filepath}: {e}")

print("\n✓ All imports updated!")
