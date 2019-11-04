# content of test_sysexit.py
import pytest


def f():
    raise SystemExit(9)


def test_mytest():
    with pytest.raises(SystemExit):
        f()