import getpass
import tkinter as tk
import xlsxwriter
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F


def get_nornir_credentials():
    username = input("Please enter domain username: ")
    password = getpass.getpass()
    hotel_code = input("Please enter hotel code: ")
    return (username, password, hotel_code)


def initialize_nornir(username, password):
    nr = InitNornir(config_file="config.yaml")
    nr.inventory.defaults.username = username
    nr.inventory.defaults.password = password
    return nr


def get_vlan_info(task):
    output = task.run(task=netmiko_send_command, command_string="show vlan brief")
    vlans = output.result.splitlines()[2:-1]
    vlan_info = []
    for vlan in vlans:
        vlan_info.append({
            "name": vlan[0:40].strip(),
            "vlan_id": vlan[0:4].strip(),
            "status": vlan[28:].strip()
        })
    return vlan_info


def write_to_excel(file, hostname, vlans):
    # Truncate the hostname to fit within 31 characters
    truncated_hostname = hostname[:31]
    
    worksheet = file.add_worksheet(truncated_hostname)
    header_format = file.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#00478B'})
    header_format.set_align('center')
    header_format.set_align('vcenter')
    worksheet.write(0, 0, "VLAN Name", header_format)
    worksheet.write(0, 1, "VLAN ID", header_format)
    worksheet.write(0, 2, "Status", header_format)
    for i, vlan in enumerate(vlans):
        worksheet.write(i + 1, 0, vlan['name'])
        worksheet.write(i + 1, 1, vlan['vlan_id'])
        worksheet.write(i + 1, 2, vlan['status'])


def main():
    username, password, hotel_code = get_nornir_credentials()
    nr = initialize_nornir(username, password)
    devices = nr.filter(F(hotel_code=hotel_code))

    workbook = xlsxwriter.Workbook(f"{hotel_code}_vlans.xlsx")

    for device in devices.inventory.hosts.values():
        hostname = device.name
        result = nr.run(task=get_vlan_info, name=hostname)
        
        # Print the results for debugging
        print(f"Results for {hostname}: {result}")
        
        # Check if the hostname exists in the result dictionary
        if hostname in result:
            vlans = result[hostname].result
            write_to_excel(workbook, hostname, vlans)
        else:
            print(f"No results found for {hostname}")

    workbook.close()

if __name__ == "__main__":
    main()