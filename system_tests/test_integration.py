import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from integration.run_full_pipeline import run_pipeline

def test_full_pipeline_integration():
    """
    Executes the full pipeline end-to-end to verify that all engines
    can communicate with the DB and pass their data forward correctly.
    This will massively boost our test coverage since it hits the 
    facades and repository logic.
    """
    success = run_pipeline()
    assert success is True
