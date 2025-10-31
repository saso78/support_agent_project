import json
from typing import List, Dict, Any
import os

class ScenarioLoader:
    def __init__(self, scenarios_dir: str):
        self.scenarios_dir = scenarios_dir

    def load_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """
        Load a single test scenario from a JSON file.
        
        Args:
            scenario_name: Name of the scenario file (without .json extension)
            
        Returns:
            Dictionary containing the scenario data
        """
        file_path = os.path.join(self.scenarios_dir, f"{scenario_name}.json")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Scenario file not found: {file_path}")
            
        with open(file_path, 'r') as f:
            return json.load(f)
            
    def load_all_scenarios(self) -> List[Dict[str, Any]]:
        """
        Load all test scenarios from the scenarios directory.
        
        Returns:
            List of dictionaries containing scenario data
        """
        scenarios = []
        
        for file_name in os.listdir(self.scenarios_dir):
            if file_name.endswith('.json'):
                scenario_path = os.path.join(self.scenarios_dir, file_name)
                try:
                    with open(scenario_path, 'r') as f:
                        scenario = json.load(f)
                        scenario['_filename'] = file_name  # Add source filename
                        scenarios.append(scenario)
                except Exception as e:
                    print(f"Error loading scenario {file_name}: {str(e)}")
                    
        return scenarios
        
    def validate_scenario(self, scenario: Dict[str, Any]) -> bool:
        """
        Validate that a scenario contains all required fields.
        
        Args:
            scenario: Dictionary containing scenario data
            
        Returns:
            True if scenario is valid, False otherwise
        """
        required_fields = ['name', 'description', 'inputs', 'expected_outputs']
        
        return all(field in scenario for field in required_fields)