from setuptools import setup

setup(
    name="lis_autocontent",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "certifi==2022.5.18.1",
        "charset-normalizer==2.0.12",
        "click==8.1.3",
        "idna==3.3",
        "PyYAML==6.0",
        "requests==2.27.1",
        "urllib3==1.26.9",
    ],
    scripts=[
        "scripts/lis_autocontent.py",
        "scripts/process_collections.py",
        "scripts/lis_cli.py",
    ],
    entry_points={
        "console_scripts": [
            "lis-autocontent = lis_autocontent:cli_entry_point",
        ]
    },
)
