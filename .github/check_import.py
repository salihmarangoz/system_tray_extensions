
import os
from pathlib import Path


def test_imports(path):
    print("Testing file:", path)

    with open(path) as f:
        lines = f.readlines()

    for l in lines:
        if "#check_import" in l or "# check_import" in l:
            l_ = l.strip()
            try:
                exec(l_)
            except:
                print("ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!")

def main():
    project_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

    is_error = False
    for path in Path(project_path).rglob('*.py'):
        if not "ste_env" in str(path) and not "check_import.py" in str(path):
            test_imports(path)

if __name__ == '__main__':
    main()