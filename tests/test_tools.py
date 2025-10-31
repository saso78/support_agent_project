import unittest
from unittest.mock import MagicMock, patch
import os
from tools.file_tools import FileTools
from tools.web_tools import WebTools
from tools.system_tools import SystemTools
from tools.rag_tools import RAGTools
from core.rag import RAGSystem

class TestTools(unittest.TestCase):
    def setUp(self):
        self.file_tools = FileTools()
        self.web_tools = WebTools()
        self.system_tools = SystemTools()
        self.mock_rag = MagicMock(spec=RAGSystem)
        self.mock_rag.query = MagicMock(return_value="Test result")
        self.rag_tools = RAGTools(rag_system=self.mock_rag)

    @patch('os.path.exists')
    def test_file_tools(self, mock_exists):
        """Test file operations."""
        mock_exists.return_value = True
        
        # Test file reading
        test_content = "Test content"
        mock_open = MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = test_content
        
        with patch('builtins.open', mock_open):
            content = self.file_tools.read_file("test.txt")
            self.assertEqual(content, test_content)

        # Test file writing
        mock_open = MagicMock()
        with patch('builtins.open', mock_open) as mock_file:
            self.file_tools.write_file("test.txt", "New content")
            mock_file.assert_called_once_with("test.txt", "w")

    @patch('requests.get')
    def test_web_tools(self, mock_get):
        """Test web operations."""
        mock_response = MagicMock()
        mock_response.text = "Web content"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        content = self.web_tools.fetch_url("http://test.com")
        self.assertEqual(content, "Web content")
        mock_get.assert_called_once_with("http://test.com")

    def test_system_tools(self):
        """Test system operations."""
        # Test disk space check
        with patch('shutil.disk_usage') as mock_usage:
            mock_usage.return_value = (100, 50, 50)
            space = self.system_tools.get_disk_space()
            self.assertIsInstance(space, dict)
            self.assertIn('total', space)
            self.assertIn('used', space)
            self.assertIn('free', space)

    def test_rag_tools(self):
        """Test RAG operations."""
        test_query = "test query"
        
        result = self.rag_tools.query(test_query)
        self.assertEqual(result, "Test result")
        self.mock_rag.query.assert_called_once_with(test_query, 3)

if __name__ == '__main__':
    unittest.main()