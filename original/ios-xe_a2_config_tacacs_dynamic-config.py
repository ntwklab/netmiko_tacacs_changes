from netmiko import ConnectHandler
import getpass
import csv
import pandas as pd



def open_csv():
    # Create a dataframe from csv
    df = pd.read_csv('iosxe_tacacs_check_modify_config.csv', delimiter=',')
    # Create a list of tuples for Dataframe rows using list comprehension
    csv_data = [tuple(row) for row in df.values]
    print("\n")
    return csv_data


def create_device_list(csv_data, tacacs_pass, admin_pass,cisco_pass):
    i = 0
    device_list = list()
    ip_list = list()
    config_list = list()
    for device in csv_data:
        ip,hostname,username,act_config,change_config = csv_data[i]

        # Assign corerct password for username
        if username == "admin":
            user_pass = admin_pass
        elif username == "cisco":
            user_pass = cisco_pass
        else:
            user_pass = tacacs_pass

        # Iterating over the list with the devices ip addresses
        cisco_device = {
               "device_type": "cisco_ios",
               "host": ip,
               "username": username,
               "password": user_pass,
               "port": 22,
               "secret": "cisco", #this is the enable password
               "verbose": True
               }
        device_list.append(cisco_device)
        ip_list.append(ip)
        config_list.append(change_config)
        # Add 1 to i for the next device
        i += 1
    return device_list,ip_list,config_list



# Create list of IPs
def ip_list(ips_list):
    # Devices Connecting to...
    print("\nThese are the devices that we will be connecting to...")
    for ip in ips_list:
        print(f"IP Address: {ip}")
    print("\n")

def config(device_list,config_commands,i,config_file,conn_ips = [],conn_host = [],conn_out = []):
    connection = ConnectHandler(**cisco_device)
    
    config_command_file = []
    with open(config_file, "r") as f:
        config_command_file = f.read().splitlines()

    print("Config file to be applied")
    for line in config_command_file:
        print (line)
    print("\n")

    # Get device hostname & IP
    prompt = connection.find_prompt()
    hostname = prompt[0:-1]
    host_ip = cisco_device["host"]
    print(f"Hostname: {hostname}\nIP Address: {host_ip}")

    # Enable Mode Check
    prompt = connection.find_prompt()
    if ">" in prompt:
        print("Entering the enable mode ...")
        connection.enable()
    
    # Enter conf t
    if not connection.check_config_mode():
        connection.config_mode()
        print("Entering the config mode ...\n")
    

    print("Removing config...")
    # send device commands using list
    config_commands_list = config_commands[i].split('\n')

    print(config_commands[i])
    connection.send_config_set(config_commands_list)
    print("\nRemoval Complete...\n")

    print("Applying config...")
    connection.send_config_set(config_command_file)
    print("\nConfig Complete...\n")


    print("Preparing output...\n")
    print("\nGetting TACACS")
    output = connection.send_command("sh run | i tacacs|aaa") # swap for iosv12/v15
    show_config = output

    """
    show_config_list = []
    if show_config == "":
        show_config = False
    else:
        output_list = show_config.splitlines()
        for line in output_list:
            if "SNMP-RO-ACL" in line:
                show_config_list.append(line)
        output = "\n".join(show_config_list)
    """
   
    # Closing the connection
    print("\nClosing connection")
    connection.disconnect()
    print("#" * 30 +"\n")

    # Return 3 lists, lists sit outside
    conn_ips.append(host_ip)
    conn_host.append(hostname)
    conn_out.append(output)
    return conn_ips,conn_host,conn_out

def write_csv(conn_ips, conn_host, conn_out):
    # Output device IP, hostname and output var to a CSV
    # No iterables are passed
    result = zip()

    # Two iterables are passed
    result = zip(conn_ips, conn_host, conn_out)

    # Converting itertor to set
    result_set = list(result)

    # Output
    with open("iosxe_tacacs_dynamic_config.csv", "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["IP Address", "Hostname", "TACACS"])

        for e in result_set:
            csv_writer.writerow(e)

    print("CSV written out")



if __name__ == "__main__":

    # Open CSV
    csv_data = open_csv()

    print("Please Enter your TACACS password")
    tacacs_pass = getpass.getpass()
    print("Please Enter admin password")
    admin_pass = getpass.getpass()
    print("Please Enter the cisco user password")
    cisco_pass = getpass.getpass()
    print("\n")


    config_file = input("Please enter the file name of the config file to apply to devices: ")

    # Create the device list
    # This needs a if statment here to pass in the corret password
    device_list,ips_list,config_list = create_device_list(csv_data, tacacs_pass, admin_pass,cisco_pass)
    ip_list(ips_list)

    # How to get config into the device, using the correct element of the list???????????
    # Config is in a speerate list called config_list now
    # Need a way to ensure that each line of that config_list is applied to the correct device in the device list i++ ish
    # Try config
    error_ips = []
    i = 0
    for cisco_device in device_list:
        try:
            conn_ips,conn_host,conn_out = config(cisco_device,config_list,i,config_file)
            i += 1 
        except:
            error = cisco_device["host"]
            print(f"There is an error connecting to {error}" )
            print("Continuing...\n")
            error_ips.append(cisco_device["host"])
            i += 1 

    # Print IPs with errors
    if error_ips != []:
        for ip in error_ips:
            print(f"Error connecting to {ip}")
            with open ("iosxe_TACACS-config_Connection_Error_IPs.txt", "a") as f:
                f.write(ip + "\n")

    # Write Output
    if "conn_ips" in globals():
        write_csv(conn_ips, conn_host, conn_out)
        
