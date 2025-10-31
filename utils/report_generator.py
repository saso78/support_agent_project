from typing import Dict, List
import json
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_evaluation_report(self, 
                                 results: List[Dict], 
                                 metadata: Dict = None) -> str: # type: ignore
        """
        Generate a detailed evaluation report from test results.
        
        Args:
            results: List of test results with metrics
            metadata: Additional information about the evaluation
            
        Returns:
            Path to generated report file
        """
        if metadata is None:
            metadata = {}
            
        report = {
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
            "results": results,
            "summary": self._generate_summary(results)
        }
        
        filename = f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
            
        return filepath
        
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics from results."""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get('passed', False))
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "average_scores": self._calculate_average_scores(results)
        }
        
    def _calculate_average_scores(self, results: List[Dict]) -> Dict:
        """Calculate average scores across all metrics."""
        if not results:
            return {}
            
        all_metrics = {}
        for result in results:
            for metric, value in result.get('metrics', {}).items():
                if isinstance(value, (int, float)):
                    if metric not in all_metrics:
                        all_metrics[metric] = []
                    all_metrics[metric].append(value)
                    
        return {
            metric: sum(values) / len(values)
            for metric, values in all_metrics.items()
        }