import unittest
from tools.webParseTool import DrugPriceLookupTool

# To run all tests from main dir:      python -m unittest discover
# To run just this test from main dir: python -m unittest tests/testWebParseTool.py

class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = DrugPriceLookupTool()
    
    def testWebParse(self):
        actual = {'found': True, 'query': 'metformin', 'count': 3, 'results': [{'medication_name': 'Metformin', 'brand_name': 'Glucophage', 'generic': True, 'form': 'Tablet', 'strength': '1000mg', 'quantity': 1, 'pack_size': 'Unknown', 'pack_units': 'ea', 'price_per_unit': '$0.019', 'total_price': '$0.019', 'ndc': '67877056310', 'url': 'https://www.costplusdrugs.com/medications/metformin-1000mg-tablet/', 'insurance_eligible': 'Yes', 'auto_refill': True}, {'medication_name': 'Metformin', 'brand_name': 'Glucophage', 'generic': True, 'form': 'Tablet', 'strength': '500mg', 'quantity': 1, 'pack_size': 'Unknown', 'pack_units': 'ea', 'price_per_unit': '$0.0106', 'total_price': '$0.0106', 'ndc': '67877056110', 'url': 'https://www.costplusdrugs.com/medications/metformin-500mg-tablet/', 'insurance_eligible': 'Yes', 'auto_refill': True}, {'medication_name': 'Metformin', 'brand_name': 'Glucophage', 'generic': True, 'form': 'Tablet', 'strength': '850mg', 'quantity': 1, 'pack_size': 'Unknown', 'pack_units': 'ea', 'price_per_unit': '$0.0184', 'total_price': '$0.0184', 'ndc': '67877056210', 'url': 'https://www.costplusdrugs.com/medications/metformin-850mg-tablet/', 'insurance_eligible': 'Yes', 'auto_refill': True}]}
        result = self.tool._run("metformin", max_results=3)
        
        self.assertEqual(result, actual)
        
    def testWebParseFailure(self):
        actual = {'found': False, 'query': 'nonexistent_drug_xyz', 'message': "No medications found matching 'nonexistent_drug_xyz'. Try a different spelling/generic name", 'results': []}
        result = self.tool._run("nonexistent_drug_xyz", max_results=3)
        
        self.assertEqual(result, actual)
    
if __name__ == "__main__":
    unittest.main()
