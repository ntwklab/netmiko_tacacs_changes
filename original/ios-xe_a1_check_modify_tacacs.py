from netmiko import ConnectHandler
import getpass
import csv
import pandas as pd



def open_csv():
    # Create a dataframe from csv
    df = pd.read_csv('cisco_check_ssh_usernames_output.csv', delimiter=',')
    # Create a list of tuples for Dataframe rows using list comprehension
    csv_data = [tuple(row) for row in df.values]
    print("\n")
    return csv_data


def create_device_list(csv_data, tacacs_pass, admin_pass, cisco_pass):
    i = 0
    device_list = list()
    ip_list = list()
    for device in csv_data:
        ip,hostname,username = csv_data[i]

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
        # Add 1 to i for the next device
        i += 1
    return device_list,ip_list

# Create list of IPs
def ip_list(ips_list):
    # Devices Connecting to...
    print("\nThese are the devices that we will be connecting to...")
    for ip in ips_list:
        print(f"IP Address: {ip}")
    print("\n")

def config(device_list,conn_ips = [],conn_host = [],conn_user = [],conn_out = [],conn_out2 = []):
    connection = ConnectHandler(**cisco_device)

    # Get device hostname & IP
    prompt = connection.find_prompt()
    hostname = prompt[0:-1]
    host_ip = cisco_device["host"]
    host_username = cisco_device["username"]
    print(f"Hostname: {hostname}\nIP Address: {host_ip}")

    # Enable Mode Check
    prompt = connection.find_prompt()
    if ">" in prompt:
        print("Entering the enable mode ...")
        connection.enable()


    print("\nGetting AAA & TACACS")
    output = connection.send_command("sh run | i tacacs|aaa") # swap from include to sectin for v12 or 15+
    
    show_tacacs = connection.send_command("sh run | i tacacs|aaa")
    
    show_tacacs_list = []
    if show_tacacs == "":
        show_tacacs = False
    else:
        output_list = show_tacacs.splitlines()
        for line in output_list:
            if "source-interface" in line:
                continue
            elif "directed-request" in line:
                continue
            elif "permit" in line:
                continue
            elif "new-model" in line:
                continue
            elif "forward-protocol" in line:
                continue
            # elif "session-id" in line:
            #     continue
            elif "config-commands" in line:
                continue
            elif line == "":
                continue
            elif "aaa accounting system" in line:
                show_tacacs_list.append("no aaa accounting system default")
            else:
                show_tacacs_list.append("no " + line)
        # print(show_tacacs_list)
        output2 = "\n".join(show_tacacs_list)
    
    """
    no_tacacs = []
    if show_tacacs == False:
        print(" Tacacs not configured")
        no_tacacs.append(cisco_device["host"])
    else:
        print("\nGetting tacacs-RO-ACL Config")
        show_tacacs_acl = connection.send_command("show ip access-lists SNMP-RO-ACL")
    """

    # Closing the connection
    print("\nClosing connection")
    connection.disconnect()
    print("#" * 30 +"\n")

    # Return 3 lists, lists sit outside
    conn_ips.append(host_ip)
    conn_host.append(hostname)
    conn_user.append(host_username)
    conn_out.append(output)
    conn_out2.append(output2)
    return conn_ips,conn_host,conn_user,conn_out,conn_out2


def write_csv(conn_ips, conn_host, conn_user, conn_out, conn_out2):
    # Output device IP, hostname and output var to a CSV
    # No iterables are passed
    result = zip()

    # Two iterables are passed
    result = zip(conn_ips, conn_host,conn_user, conn_out, conn_out2)

    # Converting itertor to set
    result_set = list(result)

    # Output
    with open("iosxe_tacacs_check_modify_config.csv", "a", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["IP Address", "Hostname", "Username", "Current Config", "Removal Configuration"])

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
    print("Please Enter cisco password")
    cisco_pass = getpass.getpass()


    # Create the device list
    # This needs a if statment here to pass in the corret password
    device_list,ips_list = create_device_list(csv_data, tacacs_pass, admin_pass,cisco_pass)
    ip_list(ips_list)


    # Try config
    error_ips = []
    for cisco_device in device_list:


        try:
            conn_ips,conn_host,conn_user,conn_out,conn_out2 = config(cisco_device)
    
        except:
            error = cisco_device["host"]
            print(f"There is an error connecting to {error}" )
            print("Continuing...\n")
            error_ips.append(cisco_device["host"])
  

    # Print IPs with errors
    if error_ips != []:
        for ip in error_ips:
            print(f"Error connecting to {ip}")
            with open ("iosxe_TACACS_Connection_Error_IPs.txt", "a") as f:
                f.write(ip + "\n")

    # Write Output
    if "conn_ips" in globals():
        write_csv(conn_ips, conn_host,conn_user,conn_out,conn_out2)
        
