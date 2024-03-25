from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
import getpass


nr = InitNornir(config_file="config.yaml")
username = input("Please enter domain username: ")
password = getpass.getpass()
hotel_code = input("Please enter hotel code: ")
nr.inventory.defaults.username = username
nr.inventory.defaults.password = password
nr.inventory.defaults.data = hotel_code


def configure_cdp(task):
    result = task.run(
        task=netmiko_send_command,
        command_string="show cdp neighbor",
        use_genie=True
    )
    cdp_neighbors = result.result["cdp"]["index"]
    for neighbor in cdp_neighbors.values():
        local_interface = neighbor["local_interface"]
        remote_interface = neighbor["port_id"]
        remote_device = neighbor["device_id"]
        config_commands = [
            f"interface {local_interface}",
            f"description Connected to {remote_device} via its {remote_interface} interface"
        ]
        task.run(
            task=netmiko_send_config,
            name="Configure CDP network descriptions",
            config_commands=config_commands
        )


results = nr.run(task=configure_cdp)
print_result(results)