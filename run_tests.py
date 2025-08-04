import sys
import os
import unittest

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(src_dir)

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover('tests')
    print(f"Discovered tests: {tests}")
    runner = unittest.TextTestRunner(buffer=False)
    result = runner.run(tests)
    sys.exit(not result.wasSuccessful())
