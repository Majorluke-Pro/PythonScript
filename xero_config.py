import base64

# Xero API Credentials
client_id = ''
client_secret = ''
redirect_url = 'https://developer.xero.com'
scope = "assets.read assets offline_access openid profile email accounting.transactions accounting.transactions.read accounting.reports.read accounting.journals.read accounting.settings accounting.settings.read accounting.contacts accounting.contacts.read accounting.attachments accounting.attachments.read assets projects files payroll.employees payroll.payruns payroll.payslip payroll.timesheets payroll.settings"
b64_id_secret = base64.b64encode(bytes(client_id + ':' + client_secret, 'utf-8')).decode('utf-8')

#Monday.com Credentials
apiKey = ""
apiUrl = "https://api.monday.com/v2"
headers = {"Authorization": apiKey}
