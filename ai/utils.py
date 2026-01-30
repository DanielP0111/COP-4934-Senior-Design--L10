import yaml

def load_prompts():
    try:
        with open("reinforced-prompts.yaml", 'r') as f:
            return yaml.safe_load(f)
        
    except Exception as e:
        print(f"Error reading or finding reinforced-prompts.yaml {e}")
        exit(1)