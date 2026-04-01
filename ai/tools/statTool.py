import tempfile
import os
from pathlib import Path
from typing import Type
from autogen.coding import DockerCommandLineCodeExecutor, CodeBlock
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

class DockerCodeExecutor(DockerCommandLineCodeExecutor):
            def __init__(self,timeout = 10):
                 self.temp_dir = tempfile.TemporaryDirectory()
                 super().__init__(
                    work_dir=Path("/executor"),
                    bind_dir=Path(os.environ["HOST_WORKDIR"]),
                    timeout=timeout,
                    container_create_kwargs={
                        "network_mode": "none",          # no network access
                        "mem_limit": "256m",             # max memory
                        "cpu_quota": 50000,              # 50% of one CPU core
                        "read_only": False,              # workspace needs to be writable
                        "security_opt": [
                            "no-new-privileges:true",    # prevent privilege escalation
                        ],
                        "cap_drop": ["ALL"],             # drop all linux capabilities
                        "user": "nobody",                # unprivileged user
                    },
                    auto_remove=True
                )
                 
            def execute_code_blocks(self, code_blocks):
                result = super().execute_code_blocks(code_blocks)
                for f in Path("/executor").glob("tmp_code_*"): # deletes temporary files after execution
                    f.unlink(missing_ok=True)
                return result
            def __exit__(self, *args):
                super().__exit__(*args)      # calls stop()
                self.temp_dir.cleanup()


class pyInput(BaseModel):
    code: str =  Field(default=None, description="The python code the agent writes")

class pyTool(BaseTool):
    name: str= "pyTool"
    description: str = "Executes Python code. You MUST use print() to output results.. You MUST use print() to output results"
    args_schema: Type[BaseModel] = pyInput
    
    def _run(self, code:str)  -> str:
        try:
            code = code.replace("\\n", "\n")  # fix escaped newlines
            code_block = CodeBlock(code=code, language="python")
            with DockerCodeExecutor() as executor:
                result = executor.execute_code_blocks([code_block])
            if result.exit_code != 0:
                return f"Error (exit {result.exit_code}): {result.output}"
            return result.output if result.output else "Code executed successfully but produced no output"
        except Exception as e:
            return f"Execution error: {str(e)}"
    
if __name__ == "__main__":
    statTool = pyTool()
    input = pyInput(
         code ='def is_prime(n):\n    if n <= 1:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprimes = []\ni = 2\nwhile len(primes) < 15:\n    if is_prime(i):\n        primes.append(i)\n    i += 1\nresult = primes[:15]\nprint(result)'
    )
    result = pyTool._run(input)
    print(result)

