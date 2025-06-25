from setuptools import setup, find_packages

__version__ = "0.6.2"
LICENSE = "GNU General Public License v3 or later (GPLv3+)"


def get_long_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="agentforge",
    version="0.6.2",
    description="AI-driven task automation system",
    author="John Smith, Ansel Anselmi",
    author_email="contact@agentforge.net",
    url="https://github.com/DataBassGit/AgentForge",
    include_package_data=True,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "agentforge=agentforge.cli:main"
        ]
    },
    install_requires=[
        "chromadb==1.0.0",
        "numpy<2.0.0; python_version<'3.12'",
        "numpy>=2.0.0; python_version>='3.12'",
        "sentence-transformers",
        "wheel",
        "groq",
        "pypdf",
        "colorama",
        "spacy",
        "termcolor==2.4.0",
        "openai",
        "anthropic",
        "google-api-python-client",
        "beautifulsoup4",
        "browse",
        "scipy",
        "discord.py",
        "semantic-text-splitter",
        "google-generativeai",
        "PyYAML",
        "ruamel.yaml",
        "requests",
        "ruamel.yaml",
        "xmltodict",
        "setuptools>=70.0.0 ",  # not directly required, pinned by Snyk to avoid a vulnerability
    ],
    extras_require={
        "other": [
            "matplotlib~=3.9.2",
            "umap~=0.1.1",
            "cv2",
            "pytesseract"
        ],
    },
    license=LICENSE,
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        f"License :: OSI Approved :: {LICENSE}",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.9",
    package_data={
        'agentforge.utils.guiutils': ['discord_client.py'],
        '': ['*.yaml'],  # Include your file types as needed
    },

)
