import pandas as pd
import yaml

# Read Excel file
excel_file = 'cisco_switch_info.xlsx'
df = pd.read_excel(excel_file)

# Convert DataFrame to YAML format
yaml_data = {}
for index, row in df.iterrows():
    switch_name = row['CorrectColumnNameForSwitchName']
    yaml_data[switch_name] = {
        'hostname': row['CorrectColumnNameForHostname'],
        'platform': 'cisco_ios',
        'groups': ['cisco_group', 'switch'],
        'data': {
            'vendor': 'Cisco',
            'domain': row['CorrectColumnNameForDomain'],
            'country': row['CorrectColumnNameForCountry'],
            'hotel_code': row['CorrectColumnNameForHotelCode']
        }
    }

# Write YAML data to file
with open('cisco_switch_info.yaml', 'w') as yaml_file:
    yaml.dump(yaml_data, yaml_file, default_flow_style=False)

print("YAML file has been created successfully!")
