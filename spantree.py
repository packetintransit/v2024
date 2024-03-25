from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
import getpass

def check_stp_and_loop_free(task):
    stp_summary_cmd = "show spanning-tree summary"
    stp_summary = task.run(netmiko_send_command, command_string=stp_summary_cmd)

    stp_type = "Unknown"
    for line in stp_summary.result.splitlines():
        line = line.lower()
        if "ieee" in line:
            stp_type = "STP"
        elif "rstp" in line:
            stp_type = "RSTP"
        elif "mstp" in line:
            stp_type = "MSTP"
        elif "pvst" in line:
            stp_type = "PVST"

    loop_free = "No loop detected"
    if "loopguard default" not in stp_summary.result.lower():
        loop_free = "Loopguard not enabled, potential for loops"

    return f"{task.host.name}:\nSTP Type: {stp_type}\nLoop-Free: {loop_free}\n"

def main():
    nr = InitNornir(config_file="config.yaml")
    username = input("Please enter domain username: ")
    nr.inventory.defaults.username = username
    password = getpass.getpass()
    nr.inventory.defaults.password = password
    hotel_code = input("Please enter hotel code: ")
    nr.inventory.defaults.data = {"hotel_code": hotel_code}

    targets = nr.filter(hotel_code=hotel_code)
    result = targets.run(task=check_stp_and_loop_free)

    output_filename = "stp_and_loop_free_summary.txt"
    with open(output_filename, 'w') as output_file:
        for host in result:
            output_file.write(result[host].result)
        print(f"Saved STP type and loop-free status for all switches to {output_filename}")

if __name__ == "__main__":
    main()