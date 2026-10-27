"""Run isolated verification and retain dependency/runtime evidence."""

import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

from check_test_environment import validate_test_environment


validate_test_environment(os.environ)
evidence = Path('/evidence')
evidence.mkdir(exist_ok=True)
inventory = {dist.metadata['Name']: dist.version for dist in importlib.metadata.distributions()}
(evidence / 'runtime.json').write_text(json.dumps({'python': platform.python_version(), 'packages': inventory}, indent=2))
subprocess.run([sys.executable, '-m', 'pip', 'check'], check=True)
with (evidence / 'pip-inspect.json').open('w') as report:
    subprocess.run([sys.executable, '-m', 'pip', 'inspect'], stdout=report, check=True)
arguments = sys.argv[1:] or ['tests', '--continue-on-collection-errors']
raise SystemExit(subprocess.call([
    sys.executable, '-m', 'pytest', *arguments, '-q', '-p', 'no:cacheprovider',
    '--junitxml=/evidence/tests.xml',
]))
