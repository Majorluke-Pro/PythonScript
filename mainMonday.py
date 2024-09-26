import os
import requests
import json
from xero_config import apiKey, apiUrl, headers

def run_script_1():
    query = """
    {
      boards(ids: 6479643558) {
        items_page(limit:10) {
          cursor
          items {
            id
            name
            column_values {
              column {
                title
              }
              text
              value
            }
          }
        }
      }
    }
    """

    data = {'query': query}

    try:
        r = requests.post(url=apiUrl, json=data, headers=headers)
        r.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
        response_data = r.json()

        output_list = []
        asset_counter = 0

        for board in response_data.get('data', {}).get('boards', []):
            for item in board.get('items_page', {}).get('items', []):
                item_id = item.get('id', 'N/A')
                item_name = item.get('name', 'N/A')

                # Initialize variables
                purchaseDate = 'N/A'
                purchasePrice = 0
                warrantyExpiryDate = 'N/A'
                assetTypeId = 'N/A'
                description = 'N/A'
                serialNumber = 'N/A'
                assetName = 'N/A'
                Manufacturer = 'N/A'
                Model = 'N/A'
                mainUser = 'N/A'
                location = 'N/A'
                status = 'Active'  # Default status

                for column_value in item.get('column_values', []):
                    title = column_value.get('column', {}).get('title', '')
                    text = column_value.get('text', '')

                    # Check if the column title is 'Status' and update the status variable
                    if title == 'Status':
                        status = text

                    if title == 'Purchase Date':
                        purchaseDate = text
                    elif title == 'Purchase Price':
                        try:
                            purchase_price_input = column_value.get('text', '')
                            purchasePrice = float(purchase_price_input)
                            #purchasePrice = int(purchasePrice * 0.85)  # Convert to integer after subtracting 15%
                        except ValueError:
                            pass  # Handle invalid values 
                    elif title == 'Serial Number':
                        serialNumber = text
                    elif title == 'Warranty Expiry Date':
                        warrantyExpiryDate = text
                    elif title == 'Asset Type ID':
                        assetTypeId = text
                    elif title == 'Model':
                        Model = text
                    elif title == 'Category':
                        assetName = text
                    elif title == 'Main User':
                        mainUser = text
                    elif title == 'Location':
                        if text == 'Sandton':  # Check if location is Sandton
                            location = text
                        else:
                            location = 'N/A'
                    elif title == 'Manufacturer':
                        Manufacturer = text

                # Skip the item if status is 'Removed'
                if status == 'Removed':
                    continue

                # Skip the item if the location is not Sandton
                if location != 'Sandton':
                    continue

                # Concatenate description
                description = f"{Model}, {mainUser}, {location}" if Model != 'N/A' and mainUser != 'N/A' and location != 'N/A' else description
                
                # Concatenate assetName with Manufacturer in parentheses
                assetName = f"{assetName}, ({Manufacturer}, {Model})" if assetName != 'N/A' and Manufacturer != 'N/A' and Model != 'N/A' else Model

                headers_data = {
                    "assetNumber": f"FA-{asset_counter:02}",
                    "assetName": assetName,
                    "purchaseDate": purchaseDate,
                    "purchasePrice": purchasePrice,
                    "serialNumber": serialNumber if serialNumber != 'N/A' else item_name,
                    "description": description,
                }

                output_list.append(headers_data)
                asset_counter += 1

        output_file_path = '/home/ubuntu-user1/Desktop/test.py/CombinedScript/output.json'

        # Delete file if it exists
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        with open(output_file_path, 'w') as json_file:
            json.dump(output_list, json_file, indent=4)
        print('Successfully stored assets in output.json')

    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Error: {str(e)}")

# If you want to execute this script independently, you can call run_script_1() here
if __name__ == '__main__':
    run_script_1()
