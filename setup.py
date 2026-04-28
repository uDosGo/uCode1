from setuptools import setup, find_packages

setup(
    name="ucode1",
    version="0.1.0",
    description="uCode1 - BASIC-inspired scripting language for uDos",
    author="uDos Team",
    author_email="team@udos.io",
    url="https://github.com/udos-go/ucode1",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "pygments>=2.0.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ucode1=ucode1.cli:main",
        ],
    },
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Interpreters",
    ],
)