from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="plex-mcp",
    version="1.0.0",
    author="Sandra",
    author_email="sandra@example.com",
    description="FastMCP 2.12 & MCPB package for Plex Media Server management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandra/plex-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "fastmcp>=2.10.6",
        "requests>=2.31.0",
        "plexapi>=4.15.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
        "xml2dict>=0.2.2",
    ],
    entry_points={
        "console_scripts": [
            "plex-mcp=plex_mcp.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
