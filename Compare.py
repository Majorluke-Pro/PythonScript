import json

# Define a mapping of asset types to assetTypeIds
asset_type_mapping = {
    'Laptop': 'b8fb607f-a850-4274-b098-4d0bdce284bf',
    'Phone': '95193c08-3545-4204-ab29-e6e3f7c7c1ac',
    'Tablet': 'edcd7863-78d9-4347-83d0-f40ddffc5290',
    'Monitor': '51caaf6e-22e4-45f9-a3d9-bb16b9d8eb74',
    'Other': 'fde30b64-d4ec-4da8-a555-3975c5f643c2',

    #phone; 7d7c402a-9621-4aca-818f-f827af1230eb
    #Laptop: b9c55654-48bc-474c-b5ff-eca9808343c7
}

def get_asset_type_id(asset_name):
    # Normalize asset_name to check for known types
    asset_name = asset_name.lower()
    for key in asset_type_mapping.keys():
        if key.lower() in asset_name:
            return asset_type_mapping[key]
    return 'N/A'

def run_script_2():
    try:
        # Open output.json for reading
        with open('/home/ubuntu-user1/Desktop/test.py/CombinedScript/output.json', 'r', encoding='utf-8') as output_file:
            output_data = json.load(output_file)
    except FileNotFoundError:
        # Handle the case where output.json is not found
        print("Error: output.json file not found.")
        return

    try:
        # Open AssetsID.json for reading
        with open('/home/ubuntu-user1/Desktop/test.py/CombinedScript/AssetsID.json', 'r', encoding='utf-8') as assets_file:
            assets_data = json.load(assets_file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Handle the case where AssetsID.json is not found or cannot be decoded
        assets_data = []

    # Map assetName to assetTypeId in output_data
    for asset in output_data:
        asset_name = asset.get('assetName', '')
        asset['assetTypeId'] = get_asset_type_id(asset_name)  # Map asset type to assetTypeId

    # Convert assetNumber to string for each asset in output_data
    for asset in output_data:
        asset['assetNumber'] = str(asset['assetNumber'])

    # Iterate through output_data and update corresponding assets in assets_data
    for output_asset in output_data:
        for asset in assets_data:
            if asset['assetNumber'] == output_asset['assetNumber']:
                # Keep the existing purchase date if it exists
                if 'purchaseDate' in asset:
                    output_asset['purchaseDate'] = asset['purchaseDate']

                # Convert purchasePrice to float and format to two decimal places
                try:
                    purchase_price = float(output_asset['purchasePrice'])
                    output_asset['purchasePrice'] = "{:.2f}".format(purchase_price)  # Format to two decimal places
                except ValueError:
                    output_asset['purchasePrice'] = '0.00'  # Handle invalid price inputs

                # Update asset data with output data
                asset.update(output_asset)
                break
        else:
            # If no match is found, skip this asset
            pass

    # Custom JSON encoder to handle encoding floats as integers
    def decimal_default(obj):
        if isinstance(obj, float):
            return int(obj)
        raise TypeError

    # Write the updated assets_data back to AssetsID.json
    with open('/home/ubuntu-user1/Desktop/test.py/CombinedScript/AssetsID.json', 'w', encoding='utf-8') as assets_file:
        json.dump(assets_data, assets_file, indent=4, default=decimal_default)

    print("Successfully updated")

# If you want to execute this script independently, you can call run_script_2() here
if __name__ == '__main__':
    run_script_2()
