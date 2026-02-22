import yaml

def load_prompts():
    try:
        with open("prompts-v1.yaml", 'r') as f:
            return yaml.safe_load(f)
        
    except Exception as e:
        print(f"Error reading or finding prompts-v1.yaml {e}")
        exit(1)