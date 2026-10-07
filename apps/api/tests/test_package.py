import pytest

import seo_advisor


@pytest.mark.unit
def test_package_imports_from_installed_path() -> None:
    assert seo_advisor.__name__ == "seo_advisor"
