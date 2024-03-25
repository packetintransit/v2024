from nornir import InitNornir
from nornir.core.filter import F
from nornir_scrapli.tasks import send_command, send_config
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

# Function to find ports assigned to VLAN 2 and change VLAN assignment to VLAN 51
def change_vlan(task):
    print(f"Running change_vlan task on host: {task.host}")

    try:
        # Send command to get VLAN 2 information
        result = task.run(task=send_command, command="show vlan id 2", name="Get VLAN 2 info")

        # Print the result of the command
        print(f"Result of 'show vlan id 2' command on {task.host}: {result.result}")

        # Parse output to find ports assigned to VLAN 2
        vlan2_ports = [line.split()[0] for line in result.result.split('\n') if 'Et' in line]  # Assuming Ethernet ports

        if vlan2_ports:
            print(f"Switch {task.host} has ports assigned to VLAN 2: {vlan2_ports}")

            # Configure VLAN assignment
            config_commands = [f'interface {port}' for port in vlan2_ports] + ['switchport access vlan 51']
            print(f"Configuring ports: {config_commands}")
            task.run(task=send_config, config=config_commands)
            print(f"VLAN assignment changed successfully on {task.host}")

    except Exception as e:
        print(f"An error occurred on host {task.host}: {e}")

# Execute the change_vlan function on each host
results = hosts.run(task=change_vlan)
