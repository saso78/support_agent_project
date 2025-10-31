import os
from typing import List, Optional

class FileTools:
    @staticmethod
    def read_file(path: str, max_size: Optional[int] = None) -> str:
        """
        Read contents of a file safely.
        
        Args:
            path: Path to the file
            max_size: Maximum number of bytes to read
            
        Returns:
            File contents as string
        """
        try:
            if not os.path.exists(path):
                return f"❌ File not found: {path}"
                
            if not os.path.isfile(path):
                return f"❌ Not a file: {path}"
                
            with open(path, "r", encoding="utf-8") as f:
                if max_size:
                    content = f.read(max_size)
                else:
                    content = f.read()
                return content
        except Exception as e:
            return f"❌ Error reading file: {str(e)}"
    
    @staticmethod
    def write_file(path: str, content: str) -> str:
        """
        Write content to a file safely.
        
        Args:
            path: Path to the file
            content: Content to write
            
        Returns:
            Success/error message
        """
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return "✅ File written successfully"
        except Exception as e:
            return f"❌ Error writing file: {str(e)}"
    
    @staticmethod
    def list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
        """
        List files in a directory, optionally filtering by pattern.
        
        Args:
            directory: Directory to list
            pattern: Optional glob pattern to filter files
            
        Returns:
            List of file paths
        """
        try:
            if pattern:
                import glob
                files = glob.glob(os.path.join(directory, pattern))
            else:
                files = [
                    os.path.join(directory, f)
                    for f in os.listdir(directory)
                    if os.path.isfile(os.path.join(directory, f))
                ]
            return sorted(files)
        except Exception as e:
            print(f"❌ Error listing files: {str(e)}")
            return []
