import ctypes as ct 

import pathlib 

rlib_path = pathlib.Path(__file__).parent.joinpath("librlib.so").absolute()

rlib = ct.cdll.LoadLibrary(rlib_path)
rlib.rliza_validate.argtypes = [ct.c_char_p]

def force_bytes(data):
    if type(data) == str:
        return data.encode('utf-8')
    elif type(data) == bytes:
        return data
    return None

def json_count(data):
    count = 0
    data = force_bytes(data)
    if not data:
        return 0
    while True:
        result = rlib.rliza_validate(data)
        if not result:
            break
        data = data[result:]
        count += 1
    return count 

def json_length(data):
    count = 0
    data = force_bytes(data)
    if not data:
        return 0
    return rlib.rliza_validate(data)


import unittest 

class RlibTestCase(unittest.TestCase):
    
    def test_json_count(self):
        self.assertEqual(json_count("{}[][]{"), 3)
        self.assertEqual(json_count("{}[][]{}"), 4)
    
    def test_json_length(self):
        self.assertEqual(json_length("{"),0)
        self.assertEqual(json_length("{}"),2)
        self.assertEqual(json_length("{}{}"),2)
        self.assertEqual(json_length("{}{}["),2)

def test():
    suite = unittest.TestLoader().loadTestsFromTestCase(RlibTestCase)
    runner = unittest.TextTestRunner()
    runner.run(suite) 

if __name__ == '__main__':
    test()
