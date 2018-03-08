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
    strip_ws = True
    expected_output = ''
    
    def __init__(self, bin, name, inputs, exp_out, strip_ws):
        self.bin_path = bin
        self.inputs = inputs
        self.name = name
        self.expected_output = exp_out
        self.strip_ws

    def run(self):
        args = [self.bin_path]
        for arg in self.inputs:
            args.append(arg)
        try:
            out = bytes.decode(subprocess.check_output(args))
            if self.strip_ws:
                out = out.strip()
        except subprocess.CalledProcessError as e:
            return (False, e.returncode, e.output if not self.strip_ws else e.output.strip())
        return (out == self.expected_output, 0, out)

def print_help():
    print('bintest (internal) v1.\n\tuse "run" to run tests or "create" to create a test.')

def current_ms():
    return int(round(time.time() * 1000))

def is_proper_dir(dir):
    def file_exists(origin, name): # used to check if there is a manifest.
        return os.path.exists(os.path.join(origin, name))
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
        for dir in os.listdir(path):
            dir = os.path.join(path, dir)
            if is_proper_dir(Path(dir).resolve()):
                tests = []
                with open(os.path.join(dir, 'manifest.json'), 'r') as f:
                    data = json.loads(f.read())
                    for test in data['tests']:
                        bin_path = Path(os.path.join(dir, data['bin'])).resolve()
                        with open(os.path.join(dir, test['output']), 'r') as o:
                            ws = test['strip_ws']
                            tests.append(Test(str(bin_path), test['name'], test['inputs'], o.read().strip() if ws else o.read(), ws))
                print('Running {} tests for module "{}".'.format(len(tests), os.path.basename(dir)))
                before_testing = current_ms()
                pass_count = 0
                for test in tests:
                    (passed, code, out) = test.run()
                    if passed:
                        pass_count += 1
                        print('\t"{}" Succeeded'.format(test.name))
                    else:
                        print('\t"{}" Failed{}'.format(test.name, '\n\tAbnormal Exit code: {}'.format(code) if code != 0  else ''))
                        print('\tExpected: "{}",\n\tGot: "{}"'.format(test.expected_output, out))
                print('Testing finished after {} ms. {} tests failed, {} succeeded.'.format(current_ms() - before_testing, len(tests) - pass_count, pass_count ))
    elif command.lower() == 'create':
        def query(what, depth=2):
            return str(input('{}{}? '.format(' ' * depth, what)))

        def add_test():
            test = {}
            test['name'] = query('Test name', depth=4)
            test['inputs'] = list(map(lambda x: x.strip(), query('Inputs (separated by commas)', depth=4).split(',')))
            test['output'] = query('Expected output file', depth=4)
            test['strip_ws'] = query('Strip whitespace [y/n]', depth=4).lower() == 'y'
            return test
        options = {
            'tests': []
        }
        options['bin'] = query('Location of executable')
        add_tests = True
        while add_tests:
            options['tests'].append(add_test())
            add_tests = query('Add another test [y/n]', depth=1).lower() == 'y'
        with open(os.path.join(path, 'manifest-{}.json'.format(current_ms())), 'w+') as f:
            f.write(json.dumps(options))
            print('Saved test configuration to "{}".\nMake sure to rename your manifest.json!'.format(os.path.basename(f.name)))
    else:
        print_help()

main()
