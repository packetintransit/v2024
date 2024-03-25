import importlib
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from datetime import date
import pathlib
from nornir_netmiko.tasks.netmiko_send_command import netmiko_send_command 
import getpass

nr = InitNornir(config_file="config.yaml")
username = input("Please enter domain username: ")
nr.inventory.defaults.username = username
password = getpass.getpass()
nr.inventory.defaults.password = password
hotel_code = input("Please enter hotel code: ")
nr.inventory.defaults.data = hotel_code


def backup_configurations(task):
    commands = "show run", "show cdp neighbor detail", "show version"
    for cmd in commands:
        config_dir = "config-archive"
        date_dir = config_dir + "/" + str(date.today())
        hotel_dir = date_dir + "/" + str(hotel_code)
        command_dir = hotel_dir + "/" + cmd
        pathlib.Path(config_dir).mkdir(exist_ok=True)
        pathlib.Path(date_dir).mkdir(exist_ok=True)
        pathlib.Path(hotel_dir).mkdir(exist_ok=True)
        pathlib.Path(command_dir).mkdir(exist_ok=True)
        r = task.run(task=netmiko_send_command, command_string=cmd)
        task.run(task=write_file, content=r.result, filename=f"" + str(command_dir) + "/" + task.host.name + ".txt", )


#result = nr.run(
    #name="Creating Backup Archive", task=backup_configurations)

targets = nr.filter(hotel_code=hotel_code)
result = targets.run(name="Creating Backup Archive", task=backup_configurations)

print_result(result)