"""Repository smoke test.

Ensures the test toolchain runs in CI before any feature code lands.
Replaced/expanded by per-feature tests as Phase 0 features are built.
"""


def test_python_version_is_supported() -> None:
    import sys

    assert sys.version_info >= (3, 12)
