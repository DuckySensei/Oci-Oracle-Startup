import requests
import json 
import copy

url = 'https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=USD'

item_id = 1

response = requests.get(url)
data = json.loads(response.text)

vm_data = {"onDemandOracle": {'1000': {}}}

# Initialize the nested structure  
vm_data["onDemandOracle"]['1000'] = {} 

for item in data['items']:
  if item['serviceCategory'] == 'Compute - Virtual Machine':
      
    vm_displayName = item['displayName']
    
    for currency in item['currencyCodeLocalizations']:
      vm_prices = currency['prices'][0]['value']
    
      # Now this key exists
      vm_data["onDemandOracle"]['1000'][item_id] = {
        "displayName": vm_displayName,
        "prices": vm_prices
      }

      item_id += 1

for i in range(1001, 1035):
  vm_data["onDemandOracle"]['1000'][str(i)] = copy.deepcopy(vm_data["onDemandOracle"]['1000'])


with open('vm_data.json', 'w') as f:
    json.dump(vm_data, f, indent=2)