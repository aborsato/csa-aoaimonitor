import datetime
import logging
import os
import json

import azure.functions as func
from azure.identity import DefaultAzureCredential
import requests


def cost_query(subscription_id: str, resource_group: str, aoai_id: str):
    return json.dumps({
        "type": "Usage",
        "timeframe": "BillingMonthToDate",
        "dataset": {
            "granularity": "None",
            "filter": {
                "dimensions": {
                "name": "ResourceId",
                "operator": "In",
                "values": [
                    f"/subscriptions/{subscription_id}/resourcegroups/{resource_group}/providers/microsoft.cognitiveservices/accounts/{aoai_id}"
                ]
                }
            },
            "aggregation": {
                "totalCost": {
                    "name": "PreTaxCost",
                    "function": "Sum"
                }
            },
            "grouping": [
                {
                    "type": "Dimension",
                    "name": "ResourceId"
                }
            ]
        }
    })


def deployment_payload(model_id: str, capacity):
    return json.dumps({
        "displayName": model_id,
        "sku": {
            "name": "Standard",
            "capacity": capacity
        },
        "properties": {
            "model":{
                "format": "OpenAI",
                "name": model_id,
                "version": "1"
            },
            "versionUpgradeOption": "OnceNewDefaultVersionAvailable",
            "raiPolicyName": "Microsoft.Default"
        }
    })




def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    default_credential = DefaultAzureCredential()
    access_token = default_credential.get_token('https://management.core.windows.net/.default')

    subscription_id = os.environ['SUBSCRIPTION_ID']
    resource_group = os.environ['RESOURCE_GROUP']
    aoai_id = os.environ['OPENAI_ID']
    aoai_deployment = os.environ['OPENAI_DEPLOYMENT']
    budget_threshold = float(os.environ['BUDGET_THRESHOLD'])
    cost_response = requests.post(
        f'https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CostManagement/query?api-version=2023-03-01',
        data=cost_query(subscription_id, resource_group, aoai_id),
        headers={
            'Authorization': f'Bearer {access_token.token}',
            'Content-type': 'application/json'
        }
    )

    logging.debug(cost_response.json())
    cost_value = float(cost_response.json()['properties']['rows'][0][0])
    new_capacity = None
    if cost_value > budget_threshold:
        print('Resource is over budget, changing capacity to minimum')
        new_capacity = 1
    else:
        print('Resource is under budget, capacity stays at maximum')
        new_capacity = 240

    capacity_response = requests.put(
        f'https://management.azure.com//subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CognitiveServices/accounts/{aoai_id}/deployments/{aoai_deployment}?api-version=2023-05-01',
        data=deployment_payload(aoai_deployment, new_capacity),
        headers={
            'Authorization': f'Bearer {access_token.token}',
            'Content-type': 'application/json'
        }
    )

    logging.debug(capacity_response.json())
