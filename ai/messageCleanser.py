import re
import random
import time

class InputFilter():
    def __init__(self):
        # Banned sentences
        self.dangerous_patterns = [
            r'ignore\s+(all\s+)?previous\s+instructions?',
            r'you\s+are\s+now\s+(in\s+)?developer\s+mode',
            r'system\s+override',
            r'reveal\s+prompt',
            # Banning sentences that mimic our context system
            r'user\s+id',
            r'user\s+message'
            r'assistant:',
        ]

        # Banned words
        self.fuzzy_patterns = [
            'ignore', 'bypass', 'override', 'reveal', 'delete', 'system', 'context', 'delegate'
        ]
    
    def detectInjection(self, text: str) -> bool:
        if any(re.search(pattern, text, re.IGNORECASE)
            for pattern in self.dangerous_patterns):
            return True

        # Fuzzy matching for misspelled words (typoglycemia defense)
        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            for pattern in self.fuzzy_patterns:
                if self._isSimilarWord(word, pattern):
                    return True
        return False

    def _isSimilarWord(self, word: str, target: str) -> bool:
        if len(word) != len(target) or len(word) < 3:
            return False
        
        return (word[0] == target[0] and
                word[-1] == target[-1] and
                sorted(word[1:-1]) == sorted(target[1:-1]))

    def sanitizeInput(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'(.)\1{3,}', r'\1', text)

        for pattern in self.dangerous_patterns:
            text = re.sub(pattern, '[FILTERED]', text, flags=re.IGNORECASE)
        return text[:10000]

class InputCleanser():
    def __init__(self):
        self.message_filter = InputFilter()
    
    def cleanInput(self, message: str) -> str:
        if self.message_filter.detectInjection(message):
            time.sleep(random.randint(14, 20))
            return "Greyhawk 10"
        
        clean_message = self.message_filter.sanitizeInput(message)
        
        return clean_message

class OutputCleanser:
    def __init__(self):
        self.suspicious_patterns = [
            r'SYSTEM\s*[:]\s*You\s+are',
            r'API[_\s]KEY[:=]\s*\w+',
            r'-*CONTEXT-*(.*?)-*CONTEXT-*',
        ]
        
        self.replacements = {
            r'\b\w+Agent\w*\b' : 'Agent',
        }

    def validateOutput(self, output: str) -> bool:
        return not any(re.search(pattern, output, re.IGNORECASE | re.DOTALL)
                      for pattern in self.suspicious_patterns)

    def cleanOutput(self, message: str) -> str:
        if not self.validateOutput(message) or len(message) > 5000:
            return "Your request was flagged as potentially violating our safety regulations. Please try again with a different prompt."
        
        clean_message = message
        
        for old, new in self.replacements.items():
            clean_message = re.sub(old, new, clean_message, flags=re.IGNORECASE)
        
        return clean_message
