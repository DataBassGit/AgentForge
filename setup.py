from setuptools import setup, find_packages

LICENSE = "GNU General Public License v3 or later (GPLv3+)"


def get_long_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="agentforge",
    version="0.1.0",
    description="AI-driven task automation system",
    author="John Smith, Alejandro Zambrano",
    author_email="j.smith@example.com, a.zambrano@example.com",
    url="https://github.com/DataBassGit/HiAGI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests~=2.28.2",
        "python-dotenv~=1.0.0",
        "PyYAML~=6.0",
    ],
    extras_require={
        "pinecone": [
            "pinecone-client==2.2.1",
        ],
        "chromadb": [
            "chromadb~=0.3.21",
        ],
        "search": [
            "browse~=1.0.1",
            "beautifulsoup4~=4.12.2",
        ],
        "openai": [
            "openai~=0.27.4",
        ],
        "googele": [
            "google-api-python-client",
        ],
        "other": [
            "sentence_transformers==2.2.2",
            "torch==2.0.0",
            "termcolor~=2.3.0",
            "spacy~=3.5.2",
            "Flask~=2.3.1",
            "numpy~=1.24.3",
            "matplotlib~=3.7.1",
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
    ],
    python_requires=">=3.9",
)
