'''
find ~/Downloads/*py | parallel "python test_runner.py {}"
'''

import unittest
import os
import sys
import json


if __name__ == "__main__":

    dirname = os.path.dirname(sys.argv[1])

    outfile = sys.argv[2]

    sys.path.append(dirname)

    fn = sys.argv[1].replace(".py", "")

    basename = os.path.basename(fn)

    try:
        mod = __import__(basename)
        tf = mod.TestFunction()
        suite = unittest.TestSuite()
        method_list = [method for method in dir(mod.TestFunction) if method.startswith('test')]
        for method in method_list:
            suite.addTest(mod.TestFunction(method))
        runner = unittest.TextTestRunner()
        results = runner.run(suite)
        success = results.wasSuccessful()
    except SyntaxError:
        success = False

    with open(outfile, "a") as of:
        ou = {"fn": fn, "wasSuccessful": success}
        of.write(json.dumps(ou) + "\n")
