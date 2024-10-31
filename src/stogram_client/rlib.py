import importlib.resources as pkg_resources
import json 
import time 

def get_rlib_path():
    binary_path = pkg_resources.files('stogram_client.binaries').joinpath('librlib.so')
    return binary_path

def generate_huge_json():
    rows = []
    str_value = [str(x) for x in range(100)]
    for x in range(10000):
        data={}
        data["property_{}_str".format(x)] = str_value
        data["property_{}_int".format(x)] = x * 2
        data["property_{}_dec".format(x)] = 0.0 + x 
        data["property_{}_null".format(x)] = None
        data["property_{}_bool_true".format(x)] = True
        data["property_{}_bool_false".format(x)] = False
        data["property_{}_array"] = [str_value,x*3,0.0+x+1,None,True,False]
        rows.append(data)
    obj = dict(rows=rows)
    return json.dumps(obj)

import ctypes as ct 

import pathlib 

rlib_path = pathlib.Path(__file__).parent.joinpath(get_rlib_path()).absolute()

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
    

    json_ = generate_huge_json()
    time_start = time.time()
    print(json_length(json_))
    duration_python = time.time() - time_start 
    time_start = time.time()
    json.loads(json_)
    duration_rliza = time.time() - time_start 
    with open("large.json","w") as f:
        f.write(json_)
    print("Speed python:",duration_python,"Speed rliza:",duration_rliza)


    suite = unittest.TestLoader().loadTestsFromTestCase(RlibTestCase)
    runner = unittest.TextTestRunner()
    runner.run(suite) 

if __name__ == '__main__':
    test()
