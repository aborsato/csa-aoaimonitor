import datetime
import logging
import os

import azure.functions as func
from azure.identity import DefaultAzureCredential
import requests


def cost_query(subscription_id: str, resource_group: str, aoai_id: str):
    return {
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
    }


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    default_credential = DefaultAzureCredential()
    access_token = default_credential.get_token('https://cognitiveservices.azure.com')

    subscription_id = os.environ['SUBSCRIPTION_ID']
    resource_group = os.environ['RESOURCE_GROUP']
    aoai_id = os.environ['OPENAI_ID']
    budget_threshold = float(os.environ['BUDGET_THRESHOLD'])
    cost_response = requests.post(
        f'https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CostManagement/query?api-version=2023-03-01',
        data=cost_query(subscription_id, resource_group, aoai_id),
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    cost_value = float(cost_response.json()['properties']['rows'][0][0])
    if cost_value > budget_threshold:
        print('Resource is over budget')
    else:
        print('Resource is under budget')
