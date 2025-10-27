# setup_cython.py
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import os
import glob

PACKAGE_NAME = "Tradeunifox"
SUBPKG = "Whatsapp"
SRC_DIR = os.path.join(PACKAGE_NAME, SUBPKG)

# Files to exclude from compilation (keep as plain .py inside wheel)
EXCLUDE = {"__init__.py", "config.py", "exceptions.py", "utils.py"}

# Collect .py files to compile
py_files = []
for f in glob.glob(os.path.join(SRC_DIR, "*.py")):
    base = os.path.basename(f)
    if base in EXCLUDE:
        continue
    py_files.append(f)

extensions = []
for py in py_files:
    module_name = os.path.splitext(os.path.basename(py))[0]
    ext_name = f"{PACKAGE_NAME}.{SUBPKG}.{module_name}"
    extensions.append(Extension(ext_name, [py]))

# Compiler directives: tweak for speed/size; safe defaults set
compiler_directives = {
    "language_level": "3",
    "boundscheck": False,
    "wraparound": False,
    "cdivision": True,
}

setup(
    name=PACKAGE_NAME,
    version="0.0.1",
    author="Trade Unifox",
    packages=find_packages(),
    ext_modules=cythonize(extensions, compiler_directives=compiler_directives),
    include_package_data=True,
    install_requires=["requests"],
    python_requires=">=3.7",
)
