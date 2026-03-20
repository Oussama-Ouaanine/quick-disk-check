from setuptools import find_packages, setup

setup(
    name="quick-disk-check",
    version="1.0.0",
    description="Fast SMART-based disk screening tool with GUI and CLI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    extras_require={"dev": ["pytest>=8.0"]},
    entry_points={
        "console_scripts": [
            "quick-disk-check=quick_disk_check.cli:main",
        ]
    },
)
