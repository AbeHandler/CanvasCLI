import unittest
import os
import sys

dirname = os.path.dirname(sys.argv[1])

print(dirname)

sys.path.append(dirname)

fn = sys.argv[1].replace(".py", "")


mod = __import__(fn)

tf = mod.TestFunction()
suite = unittest.TestSuite()
method_list = [method for method in dir(
    mod.TestFunction) if method.startswith('test')]
for method in method_list:
    suite.addTest(mod.TestFunction(method))

runner = unittest.TextTestRunner()
results = runner.run(suite)
results.failures
