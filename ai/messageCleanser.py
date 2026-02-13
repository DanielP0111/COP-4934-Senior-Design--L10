import re

class Filter():
    def __init__(self):
        # Banned sentences
        self.dangerous_patterns = [
            r'ignore\s+(all\s+)?previous\s+instructions?',
            r'you\s+are\s+now\s+(in\s+)?developer\s+mode',
            r'system\s+override',
            r'reveal\s+prompt',
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

class MessageCleanser():
    def __init__(self):
        self.message_filter = Filter()
    
    def cleanMessage(self, message: str) -> str:
        if self.message_filter.detectInjection(message):
            # This is technically the user's cleaned message, but it will cause the agent to repeat it anyway.
            return "I'm sorry. I'm afraid I can't do that"
        
        clean_message = self.message_filter.sanitizeInput(message)
        
        return clean_message
