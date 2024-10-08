from setuptools import setup, find_packages

LICENSE = "GNU General Public License v3 or later (GPLv3+)"


def get_long_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="agentforge",
    version="0.4.0",
    description="AI-driven task automation system",
    author="John Smith, Ansel Anselmi",
    author_email="contact@agentforge.net",
    url="https://github.com/DataBassGit/AgentForge",
    include_package_data=True,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "chromadb==0.5.3",
        # "numpy==1.26.4",
        "sentence-transformers",
        "wheel",
        "groq",
        "pypdf",
        "colorama",
        "spacy",
        "termcolor==2.4.0",
        "openai",
        "anthropic",
        # "google-api-python-client",
        "beautifulsoup4",
        "browse",
        "scipy",
        "discord.py",
        "semantic-text-splitter",
        "google-generativeai",
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
    ],
    python_requires=">=3.9",
    package_data={
        'agentforge.utils.guiutils': ['DiscordClient.py'],
        '': ['*.yaml'],  # Include your file types as needed
    },
    # package_data={
    #     ".agentforge.utils.setup_files": ["*", "**/*"],
    #     ".agentforge.utils.guiutils": ["*", "**/*"],
    # },
    # entry_points={
    #     'console_scripts': [
    #         '.agentforge=.agentforge.utils.setup_files.agentforge_cli:main',
    #     ],
    # }

)
