import subprocess
import json
import requests
import time
from xero_config import client_id, client_secret, redirect_url, scope, b64_id_secret
from urllib.parse import parse_qs, urlparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed



# Script to fetch all Assets from Monday and store in output.json
def run_main_monday_script():
    try:
        print("Running mainMonday.py...")
        subprocess.run(['/home/ubuntu-user1/Desktop/test.py/.venv/bin/python', '/home/ubuntu-user1/Desktop/test.py/CombinedScript/mainMonday.py'])
    except Exception as e:
        print(f"Error occurred while running mainMonday.py: {e}")


# Authentication Code to access Xero API
def run_send2xero_script():
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
        json_response = response.json()

        return [json_response['access_token'], json_response['refresh_token']]

    def get_xero_tenant_id(access_token):
        tenant_info_url = 'https://api.xero.com/connections'
        headers = {'Authorization': 'Bearer ' + access_token}
        response = requests.get(tenant_info_url, headers=headers)
        tenant_info = response.json()
        xero_tenant_id = tenant_info[0]['tenantId'] if tenant_info else None
        return xero_tenant_id

    def XeroRefreshToken(refresh_token):
        token_refresh_url = 'https://identity.xero.com/connect/token'
        response = requests.post(
            token_refresh_url,
            headers={
                'Authorization': 'Basic ' + b64_id_secret,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        )
        json_response = response.json()

        new_refresh_token = json_response.get('refresh_token', '')
        if new_refresh_token:
            with open('/home/ubuntu-user1/Desktop/test.py/CombinedScript/refresh_token.txt', 'w') as rt_file:
                rt_file.write(new_refresh_token)

        return [json_response['access_token'], json_response['refresh_token']]
    
    # Script to send assets fetched from Monday.com to Xero for Creation
    def create_fixed_asset_with_retry(access_token, xero_tenant_id, asset_data):
        create_url = 'https://api.xero.com/assets.xro/1.0/Assets'

        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Xero-tenant-id': xero_tenant_id,
            'Content-Type': 'application/json'
        }

        retry_count = 0
        while retry_count < 5:  
            response = requests.post(create_url, headers=headers, json=asset_data)
            asset_number = asset_data.get('assetNumber', 'Unknown')  
            print(f"Asset Number: {asset_number}")
            print(f"Status Code: {response.status_code}")

            if response.status_code == 201: 
                return True
            elif response.status_code == 429:  
                retry_after = int(response.headers.get('Retry-After', 5))  
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                time.sleep(retry_after) 
                retry_count += 1
            else:
                print(f"Creating fixed asset: {response.status_code}")
                print(response.text)
                return False

        print("Retry limit exceeded. Exiting...")
        return False

    # Fetching Assets from Xero to get their unique ID created in Xero and storing the fetched assets in AssetsID.json
    def display_and_save_draft_assets(access_token, xero_tenant_id):
        get_assets_url = 'https://api.xero.com/assets.xro/1.0/Assets?status=DRAFT'
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Xero-tenant-id': xero_tenant_id,
        }

        formatted_assets = []  
        page = 1
        while True:
            response = requests.get(get_assets_url + f'&page={page}', headers=headers)
            if response.status_code == 200:
                draft_assets = response.json()

                if not draft_assets:
                    print("No more draft assets found.")
                    break  
                for item in draft_assets.get('items', []):
                    asset_id = item.get("assetId", "")
                    purchase_date = item.get("purchaseDate", "")
                    if purchase_date:
                        purchase_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.strptime(purchase_date, "%Y-%m-%dT%H:%M:%S"))
                    # Construct dictionary for current asset
                    asset = {
                        "assetId": asset_id,
                        "assetName": item.get("assetName", ""),
                        "assetStatus": "Draft",
                        "assetNumber": item.get("assetNumber", ""),
                        "purchaseDate": purchase_date,
                        "purchasePrice": int(item.get("purchasePrice", 0)) if item.get("purchasePrice", "") else 0,  
                        "serialNumber": item.get("serialNumber", ""),
                        "warrantyExpiryDate": "",
                        "assetTypeId": "",
                        "description": item.get("description", ""),
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
            else:
                print(f"Error, but fetched assets anyway: {response.status_code}")
                break  
        return formatted_assets  
    
    def write_asset_data_to_json(asset_data):
        json_file_path = '/home/ubuntu-user1/Desktop/test.py/CombinedScript/AssetsID.json'
        with open(json_file_path, 'w') as json_file:
            json.dump(asset_data, json_file, indent=2)
        print(f"Asset data saved to '{json_file_path}'")


     # Sending Updated Assets Back to Xero  
    def create_fixed_asset_with_retry_updated(access_token, xero_tenant_id):
        create_url = 'https://api.xero.com/assets.xro/1.0/Assets?status=DRAFT'
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Xero-tenant-id': xero_tenant_id,
            'Content-Type': 'application/json'
        }

        try:
            with open('/home/ubuntu-user1/Desktop/test.py/CombinedScript/AssetsID.json', 'r') as file:
                asset_data_list = json.load(file)
        except Exception as e:
            logging.error(f"Error loading asset data: {e}")
            return

        logger = logging.getLogger(__name__)
        logger.info("Starting asset creation...")

        def create_asset_request(asset_data):
            retry_count = 0

            while retry_count < 3:
                try:
                    response = requests.post(create_url, headers=headers, json=asset_data)
                    logger.debug(f"Status Code: {response.status_code}")
                    logger.debug("Response:")
                    logger.debug(response.text)

                    if response.status_code == 201:  # Success
                        logger.info("Asset created successfully.")
                        return response
                    elif response.status_code == 429:  # Rate limit exceeded
                        retry_after = int(response.headers.get('Retry-After', 5))
                        logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                        time.sleep(retry_after)
                    else:
                        logger.error(f"Status Code: {response.status_code}, Response: {response.text}")

                    retry_count += 1
                    logger.warning(f"Retrying the current asset... Attempt {retry_count}/3")

                except requests.exceptions.RequestException as e:
                    logger.error(f"Request failed: {e}")
                    retry_count += 1
                    logger.warning(f"Retrying the current asset... Attempt {retry_count}/3")

            return None

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_asset = {executor.submit(create_asset_request, asset): asset for asset in asset_data_list}

            for future in as_completed(future_to_asset):
                asset = future_to_asset[future]
                try:
                    response = future.result()
                    if response and response.status_code == 201:
                        logger.info("Asset created successfully in parallel.")
                    else:
                        logger.error(f"Created asset: {asset}")
                except Exception as e:
                    logger.error(f"Exception occurred for asset {asset}: {e}")

        logger.info("Finished asset creation.")

            

    # Run mainMonday.py before everything else
    run_main_monday_script()  

    old_tokens = XeroFirstAuth()
    XeroRefreshToken(old_tokens[1])
    xero_tenant_id = get_xero_tenant_id(old_tokens[0])

    # Running Script to Send Monday Assets To Xero 
    with open('/home/ubuntu-user1/Desktop/test.py/CombinedScript/output.json', 'r') as json_file:
        asset_data_list = json.load(json_file)
    for asset_data in asset_data_list:
        if not create_fixed_asset_with_retry(old_tokens[0], xero_tenant_id, asset_data):
            print("Asset creation failed after retries:", asset_data)
    formatted_assets = display_and_save_draft_assets(old_tokens[0], xero_tenant_id)
    write_asset_data_to_json(formatted_assets)

    # Run Compare.py script ( Syncs Xero Assets with Monday.com Assets)
    try:
        print("Running Compare.py script...")
        subprocess.run(['/home/ubuntu-user1/Desktop/test.py/.venv/bin/python', '/home/ubuntu-user1/Desktop/test.py/CombinedScript/Compare.py'])
    except Exception as e:
        print(f"Error occurred while running Compare.py: {e}")

    # Running Script to send back updated Assets to Xero    
    print("Resending retrieved assets...")
    for asset_data in asset_data_list:
        if not create_fixed_asset_with_retry_updated(old_tokens[0], xero_tenant_id):
            print("Asset creation success after retries:", asset_data)

if __name__ == '__main__':
    run_send2xero_script()


