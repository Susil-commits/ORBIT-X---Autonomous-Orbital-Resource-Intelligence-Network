"""Pytest configuration and global fixtures for ORBIT-X test suite."""

import warnings
import pytest

# Suppress known 3rd-party deprecation warnings (e.g., from shap/matplotlib)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module="shap.*")
warnings.filterwarnings("ignore", category=PendingDeprecationWarning, module="matplotlib.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.*")
