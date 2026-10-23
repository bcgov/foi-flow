"""Check real application import paths in a fresh, explicitly configured process."""

from pathlib import Path
import os
import subprocess
import sys
import signal
import socket
import tempfile
import time
import shutil
from urllib.error import URLError
from urllib.request import urlopen

import pytest


SERVICE_DIR = Path(__file__).resolve().parents[1]


def synthetic_environment():
    environ = {"PATH": os.environ.get("PATH", ""), "PYTHON_DOTENV_DISABLED": "1"}
    for line in (SERVICE_DIR / "tests/upgrade.env").read_text().splitlines():
        if line and not line.startswith("#"):
            key, value = line.split("=", 1)
            environ[key] = value
    environ["PYTHONPATH"] = str(SERVICE_DIR)
    return environ


@pytest.mark.parametrize("setup", [
    "from request_api import create_app; app = create_app('testing')",
    "from wsgi import APP as app",
])
def test_application_imports_and_serves_ops(setup):
    script = setup + "; client = app.test_client(); " + (
        "response = client.get('/api/healthz'); "
        "assert response.status_code == 200; "
        "assert response.get_json() == {'message': 'api is healthy'}; "
        "response = client.get('/api/readyz'); "
        "assert response.status_code == 200; "
        "assert response.get_json() == {'message': 'api is ready'}"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=SERVICE_DIR,
        env=synthetic_environment(), capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("arguments,expected", [
    (["db", "heads"], "head"),
    (["db", "--help"], "upgrade"),
    (["list_routes"], "/api/healthz"),
])
def test_management_command_interface_is_preserved(arguments, expected):
    result = subprocess.run(
        [sys.executable, "manage.py", *arguments], cwd=SERVICE_DIR,
        env=synthetic_environment(), capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert expected in result.stdout + result.stderr


@pytest.mark.parametrize('background', [False, True])
def test_entrypoint_serves_ops_and_sigterm_stops_server(background):
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    environ = synthetic_environment()
    environ['PORT'] = str(port)
    if background:
        environ.update(
            PUBLICATION_COMPLETED_CONSUMER_ENABLED='true',
            PUBLICATION_PREPUBLISHING_SCHEDULER_ENABLED='true',
            PUBLICATION_PREPUBLISHING_INTERVAL_SECONDS='1',
            PUBLICATION_WINDOW_START='00:00',
            PUBLICATION_WINDOW_END='23:59:59.999999',
            PUBLICATION_PUBLISH_STREAM_NAME='upgrade-startup-requested',
            PUBLICATION_UNPUBLISH_STREAM_NAME='upgrade-startup-unpublish',
        )
    with tempfile.TemporaryFile(mode='w+') as log:
        process = subprocess.Popen(
            ['/bin/sh', 'entrypoint.sh'], cwd=SERVICE_DIR, env=environ,
            stdout=log, stderr=log, start_new_session=True,
        )
        url = f'http://127.0.0.1:{port}/api/readyz'
        try:
            deadline = time.monotonic() + 30
            ready = False
            while time.monotonic() < deadline and process.poll() is None:
                try:
                    with urlopen(url, timeout=0.5) as response:
                        ready = response.status == 200
                        if ready:
                            break
                except (URLError, TimeoutError):
                    time.sleep(0.05)
            log.seek(0)
            assert ready, log.read()
            if background:
                log.seek(0)
                messages = log.read()
                assert 'Publication completed stream consumer started' in messages
                assert 'Publication publishing scheduler started' in messages
            process.terminate()
            process.wait(timeout=5)
            with pytest.raises(URLError):
                urlopen(url, timeout=0.5)
        finally:
            # Terminate only the process group created by this test.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=5)


def test_real_configuration_does_not_ingest_a_local_dotenv(tmp_path):
    copied = tmp_path / 'config.py'
    shutil.copy2(SERVICE_DIR / 'request_api/config.py', copied)
    (tmp_path / '.env').write_text('UPGRADE_DOTENV_SENTINEL=must-not-be-ingested\n')
    environ = {'PATH': os.environ.get('PATH', '')}
    for line in (SERVICE_DIR / 'tests/upgrade.env').read_text().splitlines():
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            environ[key] = value
    script = (
        "import os, importlib.util; assert os.getenv('PYTHON_DOTENV_DISABLED') == '1'; "
        f"spec = importlib.util.spec_from_file_location('isolated_config', {str(copied)!r}); "
        "module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); "
        "assert os.getenv('UPGRADE_DOTENV_SENTINEL') is None"
    )
    result = subprocess.run([sys.executable, '-c', script], env=environ,
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
