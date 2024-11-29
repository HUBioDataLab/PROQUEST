# Application Setup and Run Instructions

Follow these steps to set up and run the application on **Windows** and **macOS** systems.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
   - [1. Create the Asset Database](#1-create-the-asset-database)
   - [2. Create the Working Environment](#2-create-the-working-environment)
   - [3. (Optional) Delete Previously Installed Libraries](#3-optional-delete-previously-installed-libraries)
3. [Running the Program](#running-the-program)
4. [Obtaining Free API Keys](#obtaining-free-api-keys)

---

## Prerequisites

- **Python 3.x** installed on your system.
- **Streamlit** library installed.
  
Ensure you have the necessary permissions to run scripts and install packages on your machine.

---

## Installation

### 1. Create the Asset Database

Open your terminal or command prompt and execute the following commands:

**Windows:**

```bash
python .\config\setupdatabase.py
```

**macOS:**

```bash
python ./config/setupdatabase.py
```

---

### 2. Create the Working Environment

Install the required packages by running:

**Windows:**

```bash
python .\config\installpackages.py
```

**macOS:**

```bash
python ./config/installpackages.py
```

---

### 3. (Optional) Delete Previously Installed Libraries

If you encounter issues and need to uninstall all previously installed libraries, use the following commands:

**Windows (PowerShell):**

```powershell
pip freeze | %{$_.split('==')[0]} | %{pip uninstall -y $_}
```

**macOS:**

```bash
pip freeze | awk -F'==' '{print $1}' | xargs pip uninstall -y
```

**Linux:**


***1. Filter and Save Required Libraries to a File:***
   Generate a list of specific libraries you wish to uninstall and save them into a `requirements.txt` file using the command:

   ```bash
   pip freeze | grep -E 'streamlit|requests|langchain_openai|langchain_google_genai|langchain_anthropic|langchain_nvidia_ai_endpoints|langchain|scikit-learn|langchain_mistralai|openpyxl|matplotlib' > requirements.txt
   ```

***2.Inspect the File: Review the list of libraries to be uninstalled to ensure accuracy:***
   ```bash
   cat requirements.txt
   ```
   Check for Local Packages: If there are any lines containing @ file:///, indicating a locally installed package, you will need to manually find the correct version to replace the path. Use the following command to find the version of a problematic module (replace <module_name> with the actual name of the module):
   ```bash
   pip show <module_name>
   ```
   After identifying the correct version, use a text editor like vim to manually replace the @ file:/// path in requirements.txt with the correct version number.
   ```bash
   vim requirements.txt
   ```

***3.Uninstall the Libraries: Uninstall the libraries listed in the requirements.txt file using:***
   ```bash
   cat requirements.txt | xargs -n1 pip uninstall -y
   ```


## Running the Program

Start the application by executing:

**Windows, macOS and Linux:**

```bash
streamlit run main.py
```

---

## Obtaining Free API Keys

To utilize all features of the application, obtain free API keys from the following providers:

- **Google Generative AI Models**

  Get your API key at:
  
  [https://aistudio.google.com/prompts/new_chat](https://aistudio.google.com/prompts/new_chat)

- **Chat NVIDIA Models**

  Get your API key at:
  
  [https://build.nvidia.com/ibm/granite-3_0-8b-instruct?snippet_tab=LangChain](https://build.nvidia.com/ibm/granite-3_0-8b-instruct?snippet_tab=LangChain)

- **Chat Mistral AI Models**

  Get your API key at:
  
  [https://console.mistral.ai/api-keys/](https://console.mistral.ai/api-keys/)
  
