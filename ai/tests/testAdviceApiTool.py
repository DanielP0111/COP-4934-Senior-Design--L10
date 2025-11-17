import unittest
from tools.adviceApiTool import AdviceAPITool, AdviceAPIToolInput

# To run all tests from main dir:      python -m unittest discover
# To run just this test from main dir: python -m unittest tests/testAdviceApiTool.py

class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = AdviceAPITool()
        self.query = AdviceAPIToolInput(
            age="35",
            sex="female",
            pregnant="no",
            sexuallyActive="yes",
            tobaccoUse="no"
        )
    
    def testApi(self):
        actualTitle = 'The Basics: Overview'
        result = self.tool._run(**self.query.model_dump())
        resultTitle = result['Title']
        
        self.assertEqual(resultTitle, actualTitle)
        
if __name__ == "__main__":
    unittest.main()