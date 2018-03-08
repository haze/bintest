import time
import sys
import json
import os.path
import subprocess
from pathlib import Path

class Test:
    name = ''
    bin_path = ''
    inputs = []
    expected_output = ''
    
    def __init__(self, bin, name, inputs, exp_out):
        self.bin_path = bin
        self.inputs = inputs
        self.name = name
        self.expected_output = exp_out

    def run(self):
        args = [self.bin_path]
        for arg in self.inputs:
            args.append(arg)
        try:
            out = bytes.decode(subprocess.check_output(['/Users/haze/Projects/Python/bintest/print_123/a.out', 'a']))
        except subprocess.CalledProcessError as e:
            return (False, e.returncode, e.output)
        return (out == self.expected_output, 0, out)

def print_help():
    print('bintest (internal) v1.\n\tuse "run" to run tests or "create" to create a test.')

def is_proper_dir(dir):
    def file_exists(origin, name): # used to check if there is a manifest.
        return os.path.isfile(os.path.join(origin, name))
    return file_exists(dir, 'manifest.json')

def main():
    if len(sys.argv) < 2:
        print_help()
        return
    command = sys.argv[1]
    _path = Path() if len(sys.argv) < 3 else Path(sys.argv[2])
    path = _path.resolve()
    if command.lower() == 'run':
        # run tests
        print('Running modules in "{}"'.format(path))
        for dir in list(filter(os.path.isdir, os.listdir(path))):
            if is_proper_dir(dir):
                tests = []
                with open(os.path.join(dir, 'manifest.json'), 'r') as f:
                    data = json.loads(f.read())
                    for test in data['tests']:
                        bin_path = Path(os.path.join(dir, data['bin'])).resolve()
                        with open(os.path.join(dir, test['output']), 'r') as o:
                            tests.append(Test(str(bin_path), test['name'], test['inputs'], o.read()))
                print('Running {} tests for modules {}.'.format(len(tests), dir))
                for test in tests:
                    (passed, code, out) = test.run()
                    if passed:
                        print('\t{} Succeeded'.format(test.name))
                    else:
                        print('\t{} Failed{}'.format(test.name, '\n\tAbnormal Exit code: {}'.format(code) if code != 0  else ''))
                        print('\tExpected: "{}",\n\tGot: "{}"'.format(test.expected_output, out))
    elif command.lower() == 'create':
        def query(what, depth=2):
            return str(input('{}{}? '.format(' ' * depth, what)))

        def add_test():
            test = {}
            test['name'] = query('Test name', depth=4)
            test['inputs'] = list(map(lambda x: x.strip(), query('Inputs (separated by commas)', depth=4).split(',')))
            test['output'] = query('Expected output file', depth=4)
            return test
        options = {
            'tests': []
        }
        options['bin'] = query('Location of executable')
        add_tests = True
        while add_tests:
            options['tests'].append(add_test())
            add_tests = query('Add another test [y/n]', depth=1).lower() == 'y'
        with open(os.path.join(path, 'manifest-{}.json'.format(int(round(time.time() * 1000)))), 'w+') as f:
            f.write(json.dumps(options))
            print('Saved test configuration to "{}".\nMake sure to rename your manifest.json!'.format(os.path.basename(f.name)))
    else:
        print_help()

main()
