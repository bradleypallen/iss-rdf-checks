"""Test-run log: every test records one deterministic line (no timings) via
the `log` fixture; at the end of the session they are written, sorted, to
results/tests.txt so the ledger in results/ also covers the test suite.
Tests that skip (rdflib/owlrl absent) record that they skipped."""
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LINES = []


@pytest.fixture
def log(request):
    def _log(text):
        LINES.append(f"{request.node.name}: {text}")
    return _log


def pytest_runtest_logreport(report):
    if report.when == 'call' and report.outcome == 'skipped':
        LINES.append(f"{report.nodeid.split('::')[-1]}: skipped ({report.longrepr[2] if isinstance(report.longrepr, tuple) else report.longrepr})")


def pytest_sessionfinish(session, exitstatus):
    if session.config.getoption('keyword') or session.config.getoption('markexpr'):
        return                                   # partial run: do not overwrite the ledger
    out = ROOT / 'results' / 'tests.txt'
    out.write_text('\n'.join(sorted(LINES)) + f"\nsummary: {len(LINES)} test lines, exit status {int(exitstatus)}\n")
