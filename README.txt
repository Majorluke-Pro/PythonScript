Asset Sync between Monday.com and Xero

This Python script synchronizes asset data between Monday.com and Xero, a popular accounting software. It fetches asset data from Monday.com, creates new assets in Xero, retrieves the created asset IDs, and updates the assets with additional details.

Prerequisites
Before running the script, ensure you have the following:

Python 3.x installed
Access to a Monday.com account with asset data
Access to a Xero account with appropriate permissions
Required Python packages (e.g., requests, etc.) installed

Setup

Clone or download the repository containing the script.
Create a xero_config.py file in the same directory as the script with the following contents:

pythonCopy codeclient_id = 'YOUR_XERO_CLIENT_ID'
client_secret = 'YOUR_XERO_CLIENT_SECRET'
redirect_url = 'YOUR_XERO_REDIRECT_URL'
scope = 'YOUR_XERO_SCOPE'
b64_id_secret = 'YOUR_XERO_B64_ID_SECRET'
Replace the placeholders with the appropriate values from your Xero account.

Install the required Python packages by running pip install -r requirements.txt in your virtual environment.

Usage

Run the script with python send2xero.py.
Follow the prompts to authenticate with Xero and authorize the application.
The script will fetch asset data from Monday.com, create new assets in Xero, retrieve the created asset IDs, and update the assets with additional details.
The script will also run the Compare.py script to sync the assets between Monday.com and Xero.
Finally, the script will resend the updated assets back to Xero.

Files

send2xero.py: The main script that handles the asset synchronization process.
mainMonday.py: A script that fetches asset data from Monday.com.
Compare.py: A script that compares and syncs asset data between Monday.com and Xero.
output.json: A JSON file containing the asset data fetched from Monday.com.
AssetsID.json: A JSON file containing the created asset IDs and details retrieved from Xero.