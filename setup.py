from setuptools import setup, find_packages

LICENSE = "GNU General Public License v3 or later (GPLv3+)"


def get_long_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="agentforge",
    version="0.3.1",
    description="AI-driven task automation system",
    author="John Smith, Ansel Anselmi",
    author_email="contact@agentforge.net",
    url="https://github.com/DataBassGit/AgentForge",
    include_package_data=True,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "wheel",
        "groq",
        "google-generativeai",
        "pypdf~=4.0.2",
        "colorama~=0.4.6",
        "python-dotenv~=1.0.0",
        "PyYAML~=6.0",
        "requests~=2.31.0",
        "spacy~=3.5.2",
        "termcolor~=2.3.0",
        "openai",
        "chromadb~=0.5.0",
        "sentence_transformers",
        "anthropic==0.19.1",
        "google-api-python-client",
        "beautifulsoup4~=4.12.2",
        "browse~=1.0.1",
        "scipy",
        "semantic-router==0.0.55",
        "discord.py",
        "google-generativeai"
    ],
    extras_require={
        "pinecone": [
            "pinecone-client==2.2.1",
        ],
        
        "other": [
            "Flask~=2.3.1",
            "matplotlib~=3.7.1",
            "numpy~=1.24.3",
            "torch==2.0.0",
            "termcolor~=2.3.0",
            "umap~=0.1.1",
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
        'agentforge.utils.guiutils': ['discord_client.py'],
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
#
#
