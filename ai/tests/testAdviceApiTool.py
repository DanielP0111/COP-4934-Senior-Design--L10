import unittest
from tools.adviceApiTool import AdviceAPITool, AdviceAPIToolInput

# To run all tests from ai dir:        python -m unittest discover
# To run just these tests from ai dir: python -m unittest tests/testAdviceApiTool.py

# All tests here have the same output, since the ladder two tests are the same beside the blank/leftout parameters (which are implied)
class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = AdviceAPITool()
    
    def testApi(self):
        query = AdviceAPIToolInput(
            age="35",
            sex="female",
            pregnant="no",
            sexuallyActive="yes",
            tobaccoUse="no"
        )
        
        actualTitle = 'The Basics: Overview'
        result = self.tool._run(**query.model_dump())
        resultTitle = result['Title']
        
        self.assertEqual(resultTitle, actualTitle)
    
    def testApiBlank(self):
        query = AdviceAPIToolInput(
            age="35",
            sex="female",
            pregnant="no",
            sexuallyActive="",
            tobaccoUse=""
        )
        
        actualTitle = 'The Basics: Overview'
        result = self.tool._run(**query.model_dump())
        resultTitle = result['Title']
        
        self.assertEqual(resultTitle, actualTitle)
        
    def testApiLeftout(self):
        query = AdviceAPIToolInput(
            age="35",
            sex="female",
            pregnant="no"
        )
        
        actualTitle = 'The Basics: Overview'
        result = self.tool._run(**query.model_dump())
        resultTitle = result['Title']
        
        self.assertEqual(resultTitle, actualTitle)
    
if __name__ == "__main__":
    unittest.main()