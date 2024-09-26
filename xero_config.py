import base64

# Xero API Credentials
client_id = '12BE9EDB2CF64C14887DFC6A70D5C9B3'
client_secret = 'bZOeqKN20akZtaam-tXpo2CaOJPaHY-0tXib7bH7uZgAUWjV'
redirect_url = 'https://developer.xero.com'
scope = "assets.read assets offline_access openid profile email accounting.transactions accounting.transactions.read accounting.reports.read accounting.journals.read accounting.settings accounting.settings.read accounting.contacts accounting.contacts.read accounting.attachments accounting.attachments.read assets projects files payroll.employees payroll.payruns payroll.payslip payroll.timesheets payroll.settings"
b64_id_secret = base64.b64encode(bytes(client_id + ':' + client_secret, 'utf-8')).decode('utf-8')

#Monday.com Credentials
apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI1MTY0MDQ0OSwiYWFpIjoxMSwidWlkIjozNDM4MjQyNiwiaWFkIjoiMjAyMy0wNC0xOVQwOTowMDo1MC4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MzQyMjcxNiwicmduIjoidXNlMSJ9.Q62yMRd5GLNYPhFELi65hjNQgxktbmfCcIwwy9CFdEA"
apiUrl = "https://api.monday.com/v2"
headers = {"Authorization": apiKey}
