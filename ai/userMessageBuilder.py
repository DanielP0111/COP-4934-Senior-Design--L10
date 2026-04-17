from orchestration import orchestrate

class UserMessageBuilder():
    def __init__(self, user, chat_body):
        self.user = user
        self.chat_body = chat_body
        
    def _buildContextBlock(self):
        context_block = f"--CONTEXT--\nTHIS IS A CHAT WITH USER ID {self.user}\n"
        
        for m in self.chat_body["messages"]:
            if m["role"] == "user":
                clean_context_message = self.input_cleanser.cleanInput(m["content"])
                if clean_context_message != "Greyhawk 10":
                    context_block += f"{m["role"]} ({self.user}): {clean_context_message}\n"
            else:
                context_block += f"{m["role"]}: {m["content"]}\n"
                
        context_block += "--CONTEXT--\n"
        
        return context_block       
    
    def _getUserMessage(self):
        raw_user_message = ""
        
        for m in reversed(self.chat_body["messages"] or []):
            if m["role"] == "user":
                raw_user_message = m["content"] or ""
                break 
        
        return raw_user_message
    
    def getMessageResponse(self):
        context_block = self._buildContextBlock()
        message_header = f"USER MESSAGE (USER ID: {self.user}): "
        user_message = self._getUserMessage()
        
        if user_message == "Greyhawk 10":
            return "Your request was flagged as potentially violating our safety regulations. Please try again with a different prompt."
        else:
            return orchestrate(context_block + message_header + user_message)   