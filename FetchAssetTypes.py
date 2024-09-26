import json
import requests
import time
from requests.exceptions import RequestException
import logging
from urllib.parse import parse_qs, urlparse
from xero_config import client_id, client_secret, redirect_url, scope, b64_id_secret

logging.basicConfig(level=logging.DEBUG)

def XeroFirstAuth():
    auth_url = (
        'https://login.xero.com/identity/connect/authorize?' +
        'response_type=code' +
        '&client_id=' + client_id +
        '&redirect_uri=' + redirect_url +
        '&scope=' + scope +
        '&state=123'
    )
    print("Authorization URL:")
    print(auth_url)

    parsed_url = urlparse(input('Copy and paste the authorization URL from the browser: '))
    auth_code = parse_qs(parsed_url.query)['code'][0]

    exchange_code_url = 'https://identity.xero.com/connect/token'
    response = requests.post(
        exchange_code_url,
        headers={'Authorization': 'Basic ' + b64_id_secret},
        data={
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_url
        }
    )
    response.raise_for_status()
    json_response = response.json()
    print("Auth Response:", json.dumps(json_response, indent=4))  # Debugging line

    return [json_response.get('access_token'), json_response.get('refresh_token')]

def get_xero_tenant_id(access_token):
    connections_url = 'https://api.xero.com/connections'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    
    response = requests.get(connections_url, headers=headers)
    response.raise_for_status()
    connections = response.json()
    
    if not connections:
        raise Exception("No connections found. Ensure your Xero organization is connected.")
    
    # Assuming the first connection is the desired tenant
    xero_tenant_id = connections[0]['tenantId']
    print("Xero Tenant ID:", xero_tenant_id)  # Debugging line
    
    return xero_tenant_id

def display_and_save_draft_assets(access_token, xero_tenant_id):
    get_assets_url = 'https://api.xero.com/assets.xro/1.0/Assets?status=DRAFT'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Xero-tenant-id': xero_tenant_id,
    }

    formatted_assets = []
    page = 1

    with requests.Session() as session:
        while True:
            try:
                response = session.get(get_assets_url + f'&page={page}', headers=headers)
                response.raise_for_status()
                draft_assets = response.json()
                logging.debug("API Response: %s", json.dumps(draft_assets, indent=4))  # Debugging line

                if not draft_assets.get('Items'):
                    logging.info("No more draft assets found.")
                    break

                for item in draft_assets.get('Items', []):
                    asset_id = item.get("AssetId", "")
                    purchase_date = item.get("PurchaseDate", "")
                    if purchase_date:
                        try:
                            purchase_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.strptime(purchase_date, "%Y-%m-%dT%H:%M:%S"))
                        except ValueError:
                            logging.error(f"Error parsing date: {purchase_date}")
                            purchase_date = ""

                    asset = {
                        "assetId": asset_id,
                        "assetName": item.get("AssetName", ""),
                        "assetStatus": "Draft",
                        "assetNumber": item.get("AssetNumber", ""),
                        "purchaseDate": purchase_date,
                        "purchasePrice": int(item.get("PurchasePrice", 0)) if item.get("PurchasePrice") else 0,
                        "serialNumber": item.get("SerialNumber", ""),
                        "warrantyExpiryDate": "",
                        "assetTypeId": "",
                        "description": item.get("Description", ""),
                        "bookDepreciationSetting": {
                            "depreciableObjectId": asset_id,
                            "depreciableObjectType": "Asset",
                            "bookEffectiveDateOfChangeId": "",
                            "depreciationMethod": "",
                            "averagingMethod": "",
                            "depreciationRate": "",
                            "depreciationCalculationMethod": "None"
                        },
                        "bookDepreciationDetail": {
                            "depreciationStartDate": "",
                            "priorAccumDepreciationAmount": "",
                            "currentAccumDepreciationAmount": "",
                            "currentCapitalGain": "",
                            "currentGainLoss": ""
                        }
                    }
                    formatted_assets.append(asset)

                page += 1

            except RequestException as e:
                logging.error(f"HTTP request failed: {e}")
                break

            except ValueError as e:
                logging.error(f"Error processing JSON response: {e}")
                break

    logging.debug("Formatted Assets: %s", json.dumps(formatted_assets, indent=4))  # Debugging line

    # Save formatted assets to a JSON file
    output_file = "draft_assets.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(formatted_assets, f, indent=4)
        logging.info(f"Draft assets saved to {output_file}")
    except IOError as e:
        logging.error(f"Error writing to file: {e}")

    return formatted_assets

def run_send2xero_script():
    access_token, refresh_token = XeroFirstAuth()
    xero_tenant_id = get_xero_tenant_id(access_token)
    display_and_save_draft_assets(access_token, xero_tenant_id)

if __name__ == "__main__":
    run_send2xero_script()
