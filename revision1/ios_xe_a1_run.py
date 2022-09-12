import csvDeviceList
import deviceConnections
import os


basedir = os.path.abspath(os.path.dirname(__file__))

check_tacacs_csv = csvDeviceList.csv_devices()
check_tacacs_cmds_iosxe = deviceConnections.ios_xe()


# Open CSV
open_file = f'{basedir}/cisco_check_ssh_usernames_output.csv'
csv_data = check_tacacs_csv.open_csv(open_file)

# Create the device list
device_list,ips_list = check_tacacs_csv.create_device_list(csv_data)

# Try config
check_error_ips = []
checked_list = []
command = "sh run | i tacacs|aaa"
for cisco_device in device_list:

    try:
        # 1. Create the connection
        connection, hostname, host_ip, host_username = check_tacacs_cmds_iosxe.open_connection(cisco_device)

        # 2. Send commands
        print("\nGetting AAA & TACACS")
        show_tacacs = check_tacacs_cmds_iosxe.send_commands(connection, command)
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
            removal_conf = "\n".join(show_tacacs_list)

        checked_dict = {"IP Address":host_ip, "Hostname":hostname, "Username":host_username, "Current Config":show_tacacs, "Removal Config":removal_conf}      
        checked_list.append(checked_dict)

        # 3. Close Connection
        check_tacacs_cmds_iosxe.close_connection(connection)

    except:
        error = cisco_device["host"]
        print(f"There is an error connecting to {error}" )
        print("Continuing...\n")
        check_error_ips.append(cisco_device["host"])


# Print IPs with errors
if check_error_ips != []:
    for ip in check_error_ips:
        print(f"Error connecting to {ip}")
        with open (f"{basedir}/iosxe_TACACS_Check_Failure_IPs.txt", "a") as f:
            f.write(ip + "\n")

# Write Output
# if "conn_ips" in locals():
write_file = f"{basedir}/iosxe_tacacs_check.csv"
check_tacacs_csv.write_csv(write_file,checked_list)




# Ask question to continue to to making changes
config_file = input("Please enter the file name of the config file to apply to devices: ")
error_ips = []
configured_list = []
i = 0
for cisco_device in device_list:
    try:
        if cisco_device["host"] not in check_error_ips:
            
            # 1. Create connection
            connection, hostname, host_ip, host_username = check_tacacs_cmds_iosxe.open_connection(cisco_device)

            # 2. Send removal commands
            # config_remove = checked_list[i]["Removal Config"]
            config_remove = cisco_device["Removal_Config"]=checked_list[i]["Removal Config"]
            config_remove_list = []
            for line in config_remove:
                config_remove_list.append(line)
            check_tacacs_cmds_iosxe.send_config_file(connection,config_remove_list)
            
            # 3. Send config file for newtacacs.cfg
            check_tacacs_cmds_iosxe.send_config_file(connection,config_file)
            
            # 4. Send show commands to check
            print("\nGetting AAA & TACACS")
            change_tacacs = check_tacacs_cmds_iosxe.send_commands(connection, command)
            config_dict = {"IP Address":host_ip, "Hostname":hostname, "Username":host_username, "Current Config":change_tacacs}      
            configured_list.append(config_dict)

            # 3. Close Connection
            check_tacacs_cmds_iosxe.close_connection(connection)
            i += 1
    
    except:
        error = cisco_device["host"]
        print(f"There is an error connecting to {error}" )
        print("Continuing...\n")
        error_ips.append(cisco_device["host"])


# Print IPs with errors
if error_ips != []:
    for ip in error_ips:
        print(f"Error connecting to {ip}")
        with open (f"{basedir}/iosxe_TACACS_Config_Failure_IPs.txt", "a") as f:
            f.write(ip + "\n")

# Write Output
write_file = f"{basedir}/iosxe_tacacs_config.csv"
check_tacacs_csv.write_csv(write_file,configured_list)

