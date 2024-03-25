import getpass
import pandas as pd
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command


def initialize_nornir():
    nr = InitNornir(config_file="config.yaml")
    username = input("Please enter domain username: ")
    nr.inventory.defaults.username = username
    password = getpass.getpass()
    nr.inventory.defaults.password = password
    hotel_code = input("Please enter hotel code: ")
    nr.inventory.defaults.data = {"hotel_code": hotel_code}
    return nr


# Function to get MAC addresses and their connected ports
def get_mac_addresses_ports(task):
    command = "show mac address-table dynamic vlan 2"
    output = task.run(task=netmiko_send_command, command_string=command)
    lines = output.result.splitlines()

    # Parse the output lines to extract the required data
    mac_data = []
    for line in lines[1:]:  # Skip the header line
        parts = line.split()
        if len(parts) >= 4:  # Check if the line contains the required information
            vlan = parts[0]
            mac = parts[1]
            _type = parts[2]
            port = parts[3]
            mac_data.append({"VLAN": vlan, "MAC Address": mac, "Type": _type, "Port": port})

    return mac_data

def main():
    nr = initialize_nornir()
    # Run the function on all devices
    results = nr.run(task=get_mac_addresses_ports)

    # Initialize the Excel writer
    with pd.ExcelWriter("mac_addresses_ports.xlsx") as writer:
        # Save the MAC data for each switch to separate sheets
        for name, multi_result in results.items():
            print(f"Switch Name: {name}")

            # Extract the actual result data from the MultiResult
            for result in multi_result:
                if result.failed:
                    print(f"Failed to retrieve data from {name}")
                    continue

                result_data = result.result  # This should be the actual data you are interested in

                if not result_data:  # Check if result_data is not empty
                    print(f"No data retrieved from {name}")
                    continue

                print(f"Result: {result_data}")  # Print the result data for debugging

                sheet_name = f"{name} MACs"
                sheet_name = sheet_name[:31]  # Truncate sheet name to 31 characters

                # Create the DataFrame
                mac_data_df = pd.DataFrame(result_data, columns=["VLAN", "MAC Address", "Type", "Port"])
                print(mac_data_df)  # Print the DataFrame for debugging
                mac_data_df.to_excel(writer, sheet_name=sheet_name, index=False)

if __name__ == "__main__":
    main()
