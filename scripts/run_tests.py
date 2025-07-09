"""
Script to run tests
"""
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import log


def run_tests():
    """Run all tests"""
    log.info("Running tests...")
    
    try:
        # Run pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], cwd=project_root, capture_output=True, text=True)
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            log.info("All tests passed!")
        else:
            log.error(f"Tests failed with return code: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        log.error(f"Error running tests: {e}")
        return False


def run_linting():
    """Run code linting"""
    log.info("Running code linting...")
    
    try:
        # Run flake8
        result = subprocess.run([
            sys.executable, "-m", "flake8", 
            "src/", "scripts/", "main.py",
            "--max-line-length=100",
            "--ignore=E203,W503"
        ], cwd=project_root, capture_output=True, text=True)
        
        if result.stdout:
            print("Flake8 output:")
            print(result.stdout)
        
        if result.returncode == 0:
            log.info("Code linting passed!")
        else:
            log.warning("Code linting found issues")
        
        return result.returncode == 0
        
    except Exception as e:
        log.error(f"Error running linting: {e}")
        return False


def main():
    """Main function"""
    log.info("Starting test suite...")
    
    # Run linting
    linting_passed = run_linting()
    
    # Run tests
    tests_passed = run_tests()
    
    # Summary
    log.info("=== Test Summary ===")
    log.info(f"Linting: {'PASSED' if linting_passed else 'FAILED'}")
    log.info(f"Tests: {'PASSED' if tests_passed else 'FAILED'}")
    
    if tests_passed and linting_passed:
        log.info("All checks passed!")
        return 0
    else:
        log.error("Some checks failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
