from setuptools import setup, find_packages

setup(
    name="Tradeunifox",                    # PyPI package name
    version="0.0.1",                       # version number
    author="Trade Unifox",                       # author name
    author_email="contact@tradeunifox.com",# optional email
    description="Official TradeUnifox WhatsApp API module by Trade Unifox",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
