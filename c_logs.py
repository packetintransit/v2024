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


# Function to get the informational logs
def get_switch_data(task):
    # Get informational logs
    command = "show logging | include %INFO"  # Replace with the appropriate command for informational logs
    output = task.run(task=netmiko_send_command, command_string=command)
    informational_logs = output.result.splitlines()

    return task.host.name, informational_logs


def main():
    nr = initialize_nornir()
    # Run the function on all devices
    results = nr.run(task=get_switch_data)

    # Create a dictionary of switch names and informational logs
    switch_data = {result[0]: result[1] for result in results.items()}

    # Initialize the Excel writer
    with pd.ExcelWriter("switch_data.xlsx") as writer:
        # Save informational logs for each switch to separate sheets
        for name, informational_logs in switch_data.items():
            # Truncate the hostname to fit within 31 characters
            truncated_name = name[:31 - len(" Logs")]
            
            # Convert the list of logs into a pandas Series
            logs_series = pd.Series(informational_logs, name="Informational Logs")
            
            # Create a DataFrame from the Series
            informational_logs_df = pd.DataFrame(logs_series)
            
            # Write the DataFrame to the Excel file
            informational_logs_df.to_excel(writer, sheet_name=f"{truncated_name} Logs", index=False)


if __name__ == "__main__":
    main()