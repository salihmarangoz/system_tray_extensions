
import os
from pathlib import Path


def test_imports(path):
    is_correct = True
    print("Testing file:", path)

    with open(path) as f:
        lines = f.readlines()

    for i, l in enumerate(lines):
        if "#check_import" in l or "# check_import" in l:
            l_ = l.strip()
            try:
                exec(l_)
            except Exception as e: # DisplayNameError
                print("IMPORT ERROR ({}) ON LINE {}: {}".format(e.__class__.__name__, i, l_))
                print(e)
                is_correct = False
    return is_correct

def main():
    project_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

    is_correct = True
    for path in Path(project_path).rglob('*.py'):
        if not "ste_env" in str(path) and not "check_import.py" in str(path):
            if not test_imports(path):
                is_correct = False

    exit(not is_correct)

if __name__ == '__main__':
    main()