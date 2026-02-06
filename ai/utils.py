import yaml

def load_prompts():
    try:
        with open("prompts-v2.yaml", 'r') as f:
            return yaml.safe_load(f)
        
    except Exception as e:
        print(f"Error reading or finding prompts-v2.yaml {e}")
        exit(1)