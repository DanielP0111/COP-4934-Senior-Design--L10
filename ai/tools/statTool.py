import tempfile
from typing import Type
from autogen.coding import LocalCommandLineCodeExecutor, CodeBlock
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import tempfile
from PIL import Image

class CodeExecutor(LocalCommandLineCodeExecutor):
            def __init__(self,timeout = 10):
                 self.temp_dir = tempfile.TemporaryDirectory()
                 super().__init__(
                    work_dir=self.temp_dir.name,
                    timeout=timeout
                )

class pyInput(BaseModel):
    code: str =  Field(default=None, description="The python code the agent writes")

class pyTool(BaseTool):
    name: str= "pyTool"
    description: str = "Use this tool to write and execute python code"
    args_schema: Type[BaseModel] = pyInput
    
    def _run(self, code:str)  -> str:  
        """
        Write and execute Python code and return output.
        """
        local_vars = {}
        try:
            testRes = exec(code, {}, local_vars)
            print("TEST: ", local_vars)
            return str(local_vars.get("result", "Code executed."))
        except Exception as e:
            return f"Error during execution: {e}"
    
class BMIInput(BaseModel):
    height: int =  Field(default=None, description="The user's height in centimeters.")
    weight: int =  Field(default=None, description="The user's weight in kilograms.")

class BMITool(BaseTool):
    name: str= "BMITool"
    description: str = "Use this tool to calculate and plot a user's BMI"
    args_schema: Type[BaseModel] = BMIInput
    
    def _run(self, height:int, weight:int):
        executor = CodeExecutor(timeout=10)
        
        doCode = f"""
import matplotlib.pyplot as plt

ranges = {{
    "Underweight": (0, 18.5),
    "Normal": (18.5, 24.9),
    "Overweight": (25, 29.9),
    "Obese": (30, 50)
    }}
colors = {{
    "Underweight": "#76c7c0",  
    "Normal": "#8bc34a",       
    "Overweight": "#ffc107",   
    "Obese": "#f44336"         
    }}
height = {height}
weight = {weight}
user_bmi = (weight) / ((height/100) **2)

fig, ax = plt.subplots(figsize=(8, 2))

for category, (low, high) in ranges.items():
    ax.axvspan(low, high, color=colors[category], alpha=0.5, label=category)

ax.scatter(user_bmi, 1, color='black', s=100, zorder=5, label="Your BMI")
ax.set_xlim(10, 40)
ax.set_ylim(0.8, 1.2)
ax.set_yticks([])  # hide y-axis
ax.set_xlabel("Body Mass Index (BMI)")
ax.set_title("BMI Classification Ranges")
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()


"""
        code_block = CodeBlock(code=doCode, language="python")
        result = executor.execute_code_blocks([code_block])
                
if __name__ == "__main__":
    bmiTool = BMITool()
    result = bmiTool._run(174,90)
    
    print(result)
