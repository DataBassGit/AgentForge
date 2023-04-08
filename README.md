# BabyBoogaAGI
BabyBoogaAGI is an AI-powered task automation system that generates, prioritizes, and executes tasks based on a given objective. It uses Pinecone, SentenceTransformer, and the Oobabooga API for text generation to accomplish its tasks.

## Installation
1. Clone the repository:

```
git clone https://github.com/your_github_username/BabyBoogaAGI.git
cd BabyBoogaAGI
```

2. Install the required libraries:

```
pip install -r requirements.txt
```

Note: You may want to create a virtual environment to isolate the project's dependencies.

3. Set up the Oobabooga API by following the instructions in their text-generation-webui repository. (https://github.com/oobabooga/text-generation-webui) You need to download the repository and follow their setup instructions.

4. Modify the start-webui.bat file in the Oobabooga repository to match the following content:

```
@echo off

@echo Starting the API...

cd /D "%~dp0"

set MAMBA_ROOT_PREFIX=%cd%\installer_files\mamba
set INSTALL_ENV_DIR=%cd%\installer_files\env

if not exist "%MAMBA_ROOT_PREFIX%\condabin\micromamba.bat" (
 call "%MAMBA_ROOT_PREFIX%\micromamba.exe" shell hook >nul 2>&1
)
call "%MAMBA_ROOT_PREFIX%\condabin\micromamba.bat" activate "%INSTALL_ENV_DIR%" || ( echo MicroMamba hook not found. && goto end )
cd text-generation-webui

#This is the line that needs to be changed:
python server.py --auto-devices --listen --no-stream

:end
pause
```
This modification ensures that the Oobabooga API starts correctly.

5. Make sure you have a language model installed. You can either run download-models.bat and select your own, your you can download a model from huggingface directly and save it in the /oogabooga-windows/text-generation-webui/models folder.

## Usage
1. Run the main.py script to start the BabyBoogaAGI:

```
python main.py
```
This script will initialize the AI system, generate tasks, prioritize them, and execute the tasks based on the given objective.

2. Monitor the output to see the tasks being generated and executed. The script will continue running until you manually stop it.

## Contributing
Feel free to open issues or submit pull requests with improvements or bug fixes. Your contributions are welcome!

## License
This project is licensed under the MIT License. See LICENSE for more details.
