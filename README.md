# csa-aoaimonitor
Azure OpenAI quota monitor.
It will turn your OpenAI quota to minimum (1k tokens/minute) if the total spent on thet resource cross a defined threshold.

# Run locally

1. Install vscode extensions:
   - Python (`ms-python.python`)
   - Azure Functions (`ms-azuretools.vscode-azurefunctions`)
   - Azurite (`azurite.azurite`)

1. Start Azurite Storage emulator
   - `Ctrl+Shift+P`, then type `Azurite: Start`

1. Create the file `local.settings.json`
   ```json
   {
   "IsEncrypted": false,
   "Values": {
       "AzureWebJobsStorage": "UseDevelopmentStorage=true",
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "SUBSCRIPTION_ID": "VALUE HERE",
       "RESOURCE_GROUP": "VALUE HERE",
       "OPENAI_ID": "RESOURCE NAME HERE",
       "OPENAI_DEPLOYMENT": "VALUE HERE",
       "BUDGET_THRESHOLD": "VALUE HERE (in USD)"
   }
   }
   ```
1. Open the file `ChackBilling/__init__.py`

1. Run it with `F5`
   - vscode will assk to install all tooling required to run it locally.