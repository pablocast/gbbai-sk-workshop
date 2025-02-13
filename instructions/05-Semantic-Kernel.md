---
lab:
    title: 'Crear un bot usando Semantic Kernel'
    description: 'Aprende cómo crear un Agente de Semantic Kernel con Plugins Nativos'
---

# Descripción
Este ejemplo proporciona una plantilla y una guía sobre cómo desplegar un asistente virtual usando Semantic Kernel aprovechando múltiples tecnologías de Azure AI. Cubre:
- el despliegue de la infraestructura 
- creacion de data fake
- creacion del agente usando Semantic Kernel
- ejecucion del bot (ambiente local usando Bot Emulator)

# Prerequisitos
- [Python 3.11 or later version](https://www.python.org/) installed (recommended to use a separate python environment for this lab)
- [VS Code](https://code.visualstudio.com/) installed with the [Jupyter notebook extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) enabled
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed
- [An Azure Subscription](https://azure.microsoft.com/free/) with Contributor permissions
- [Access granted to Azure OpenAI](https://aka.ms/oai/access) or just enable the mock service
- [Sign in to Azure with Azure CLI](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively)
- [Bot Emulator](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-debug-emulator?view=azure-bot-service-4.0&tabs=csharp)

## [Crear Infrastructura](../lab/chat-app/infra/set_up_env.ipynb)

1. Python
```bash
# Set up a virtualenv / conda environment and activate it
cd lab/chat-app/python
pip install -r requirements.txt 
```

2. Ejecutar el [notebook](../lab/chat-app/infra/set_up.ipynb)