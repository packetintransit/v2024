from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
import getpass

# Initialize Nornir with configuration file
nr = InitNornir(config_file="config.yaml")

# Set username and password
username = input("Please enter domain username: ")
password = getpass.getpass()

# Set defaults for username and password
nr.inventory.defaults.username = username
nr.inventory.defaults.password = password

# Set hotel code
hotel_code = input("Please enter hotel code: ")

# Filter hosts based on hotel code
hosts = nr.filter(F(data__hotel_code=hotel_code))
print(f"Selected hosts: {hosts.inventory.hosts}")

# Function to change VLAN assignment for interfaces assigned to MGMT VLAN to VLAN 51
def change_vlan(task):
    print(f"\nRunning change_vlan task on host: {task.host}")

    try:
        # Send command to get VLAN information
        print(f"Sending 'show vlan brief' command to {task.host}...")
        result = task.run(task=netmiko_send_command, command_string="show vlan brief", name="Get VLAN info")
        
        # Parse output to find interfaces assigned to MGMT VLAN
        lines = result.result.split("\n")
        mgmt_ports = [line.split()[-1] for line in lines if line.startswith("2 ")]

        print(f"Ports assigned to MGMT VLAN on {task.host}: {mgmt_ports}")

        if mgmt_ports:
            print(f"Switch {task.host} has ports assigned to MGMT VLAN: {mgmt_ports}")

            # Configure VLAN assignment to VLAN 51 for each interface
            config_commands = [f"interface {port}" for port in mgmt_ports] + ["switchport access vlan 51" for _ in mgmt_ports]
            print(f"Configuring interfaces on {task.host}:\n{config_commands}")

            # Apply configuration to change VLAN assignment
            result_config = task.run(task=netmiko_send_config, config_commands=config_commands, read_timeout=120)  # Set read_timeout to 120 seconds
            
            # Check if the task was successful
            if result_config.failed:
                raise Exception(f"Failed to configure VLAN on {task.host}. Details: {result_config[0].result}")

            print(f"VLAN assignment changed successfully on {task.host}")

            # Print the list of ports that have been changed
            print(f"Changed VLAN assignment to VLAN 51 on {task.host} for the following ports: {mgmt_ports}")

    except Exception as e:
        print(f"An error occurred on host {task.host}: {e}")

# Execute the change_vlan function on each host
print("\nStarting VLAN change process...\n")
results = hosts.run(task=change_vlan)

print("\nVLAN change process completed.")
