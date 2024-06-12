from pathlib import Path
from setuptools import setup, find_packages
import re


# Package meta-data.
NAME = "HOPP"
DESCRIPTION = "Hybrid Systems Optimization and Performance Platform."
URL = "https://github.com/NREL/HOPP"
EMAIL = "dguittet@nrel.gov"
AUTHOR = "NREL"
REQUIRES_PYTHON = ">=3.8.0"

ROOT = Path(__file__).parent
with open(ROOT / "hopp" / "version.py") as version_file:
    VERSION = version_file.read().strip()

# Get package data
hopp_base_path = Path("hopp")
hopp_package_data_files = [
    *hopp_base_path.glob("tools/analysis/bos/BOSLookup.csv"),
    *hopp_base_path.glob("simulation/technologies/layout/flicker_data/*shadow.txt"),
    *hopp_base_path.glob("simulation/technologies/layout/flicker_data/*flicker.txt"),
    *hopp_base_path.glob("simulation/technologies/csp/pySSC_daotk/libs/*"),
    *hopp_base_path.glob("simulation/technologies/csp/pySSC_daotk/tower_data/*"),
    *hopp_base_path.glob("simulation/technologies/csp/pySSC_daotk/trough_data/*"),
    *hopp_base_path.glob("simulation/technologies/dispatch/cbc_solver/cbc-win64/*"),
    *hopp_base_path.glob("simulation/resource_files/*"),
    *hopp_base_path.glob("simulation/resource_files/*/*")
]

greenheart_base_path = Path("greenheart")
greenheart_package_data_files = [
    greenheart_base_path / "hydrogen" / "h2_storage" / "pressure_vessel" / "compressed_gas_storage_model_20221021" / "Tankinator.xlsx",
    *greenheart_base_path.glob("hydrogen/h2_transport/data_tables/*.csv")
]

package_data = {
    "hopp": [str(file.relative_to(hopp_base_path)) for file in hopp_package_data_files],
    "greenheart": [str(file.relative_to(greenheart_base_path)) for file in greenheart_package_data_files]
}

setup(
    name=NAME,
    version=VERSION,
    url=URL,
    description=DESCRIPTION,
    long_description=(base_path.parent / "RELEASE.md").read_text(),
    long_description_content_type='text/markdown',
    license='BSD 3-Clause',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    install_requires=(base_path.parent / "requirements.txt").read_text().splitlines(),
    tests_require=['pytest', 'pytest-subtests', 'responses']
)
