from nornir import InitNornir
from nornir_napalm.plugins.tasks.napalm_get import napalm_get 
from nornir_utils.plugins.functions import print_result
import getpass

nr = InitNornir(config_file="config.yaml")
username = input("Please enter domain username: ")
password = getpass.getpass()
hotel_code = input("Please enter hotel code: ")
nr.inventory.defaults.username = username
nr.inventory.defaults.password = password
nr.inventory.defaults.data = hotel_code

def main():
    nr = InitNornir(config_file="config.yaml")
    mac_address = "00:11:22:33:44:55"  # Change this to the MAC address you want to search for
    results = nr.run(napalm_get, getters=["lldp_neighbors"])
    for host, result in results.items():  # Iterate over hosts and their results
        if isinstance(result.result, dict):
            lldp_neighbors = result.result.get("lldp_neighbors", {})  # Get the lldp_neighbors result or an empty dictionary
            for interface, neighbor_info in lldp_neighbors.items():
                neighbor_mac = neighbor_info["remote_chassis_id"]
                if neighbor_mac == mac_address:
                    print(f"MAC address {mac_address} found on {host} interface {interface}")
                    interface_status = nr.run(
                        task=get_interface_status, interface=interface
                    )
                    print_result(interface_status)
                    interface_errors = nr.run(
                        task=get_interface_errors, interface=interface
                    )
                    print_result(interface_errors)
        else:
            print(f"No LLDP neighbors data found for host {host}.")


if __name__ == "__main__":
    main()