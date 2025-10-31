import os
import shutil
import subprocess
from typing import Dict, List, Optional, Union
import platform

class SystemTools:
    @staticmethod
    def get_disk_space(path: str = ".") -> Dict[str, int]:
        """
        Get disk space information for a given path.
        
        Args:
            path: Path to check disk space for
            
        Returns:
            Dictionary with total, used and free space in bytes
        """
        total, used, free = shutil.disk_usage(path)
        return {
            "total": total,
            "used": used,
            "free": free
        }

    @staticmethod
    def run_command(command: Union[str, List[str]], timeout: int = 30) -> Dict[str, Union[str, int]]:
        """
        Run a system command safely.
        
        Args:
            command: Command to run (string or list of arguments)
            timeout: Maximum execution time in seconds
            
        Returns:
            Dictionary with stdout (str), stderr (str) and return code (int)
        """
        try:
            result = subprocess.run(
                command,
                shell=isinstance(command, str),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """
        Get basic system information.
        
        Returns:
            Dictionary with system information
        """
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
    
    @staticmethod
    def is_process_running(process_name: str) -> bool:
        """
        Check if a process is running.
        
        Args:
            process_name: Name of the process to check
            
        Returns:
            True if process is running, False otherwise
        """
        if platform.system() == "Windows":
            command = f'tasklist /FI "IMAGENAME eq {process_name}" /NH'
        else:
            command = f'pgrep -f {process_name}'
            
        result = SystemTools.run_command(command)
        return_code = result["returncode"]
        stdout = result["stdout"]
        if not isinstance(return_code, int) or not isinstance(stdout, str):
            return False
        return return_code == 0 and bool(stdout.strip())