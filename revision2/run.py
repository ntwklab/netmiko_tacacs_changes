import csvDeviceList
import deviceConnections
import os


basedir = os.path.abspath(os.path.dirname(__file__))

check_tacacs_csv = csvDeviceList.csv_devices()
check_tacacs_cmds_iosxe = deviceConnections.BaseConn()
show_cmds = deviceConnections.CmdLibrary()


# Open CSV
open_file = f'{basedir}/cisco_check_ssh_usernames_output.csv'
csv_data = check_tacacs_csv.open_csv(open_file)

# Create the device list
device_list,ips_list = check_tacacs_csv.create_device_list(csv_data)

# Try config
check_error_ips = []
dev_ver_list = []
show_tacacs_list = []
i = 0
for cisco_device in device_list:


    try:
        # 1. Create the connection
        connection, hostname, host_ip, host_username = check_tacacs_cmds_iosxe.open_connection(cisco_device)

        # 2. Get Version commands
        print("Getting Version")
        device_version = check_tacacs_cmds_iosxe.get_version(connection)
        print(device_version)

        dev_ver_dict = {"IP Address":host_ip, 
                        "Hostname":hostname, 
                        "Username":host_username, 
                        "Device Version":device_version}      
        dev_ver_list.append(dev_ver_dict)

        #3. Show TACACS
        dev_details = dev_ver_list[i]
        show_tacacs, removal_conf = show_cmds.get_tacacs(connection, dev_details)

        show_tacacs_dict = {"IP Address":host_ip, 
                        "Hostname":hostname, 
                        "Username":host_username, 
                        "Current Config":show_tacacs, 
                        "Removal Config":removal_conf, 
                        "Device Version":device_version}      
        show_tacacs_list.append(show_tacacs_dict)

        # 4. Close Connection
        check_tacacs_cmds_iosxe.close_connection(connection)
        i += 1

    except:
        error = cisco_device["host"]
        print(f"There is an error connecting to {error}" )
        print("Continuing...\n")
        check_error_ips.append(cisco_device["host"])
        i += 1


# Print IPs with errors
if check_error_ips != []:
    for ip in check_error_ips:
        print(f"Error connecting to {ip}")
        with open (f"{basedir}/iosxe_TACACS_Check_Failure_IPs.txt", "a") as f:
            f.write(ip + "\n")

# Write Output
# if "conn_ips" in locals():
write_file = f"{basedir}/iosxe_tacacs_check.csv"
check_tacacs_csv.write_csv(write_file,show_tacacs_list)




# Ask question to continue to to making changes
ios12config_file = input("Please enter the file name of the IOS 12 config file to apply to devices: ")
ios15config_file = input("Please enter the file name of the IOS 15 config file to apply to devices: ")
iosxeconfig_file = input("Please enter the file name of the IOS XE config file to apply to devices: ")
nxosconfig_file = input("Please enter the file name of the NXOS config file to apply to devices: ")

error_ips = []
configured_list = []
i = 0
for cisco_device in device_list:
    try:
        if cisco_device["host"] not in check_error_ips:
            
            # 1. Create connection
            connection, hostname, host_ip, host_username = check_tacacs_cmds_iosxe.open_connection(cisco_device)

            # 2. Create and if based on the device type
            # config_remove = show_tacacs_list[i]["Removal Config"]
            device_type = cisco_device["Device_Version"]=show_tacacs_list[i]["Device Version"]

        # 3. Send removal commands
        # config_remove = show_tacacs_list[i]["Removal Config"]
        config_remove = cisco_device["Removal_Config"]=show_tacacs_list[i]["Removal Config"]
        config_remove_list = []
        for line in config_remove:
            config_remove_list.append(line)
        check_tacacs_cmds_iosxe.send_config_file(connection,config_remove_list)
        

        # 4. Send config file for newtacacs.cfg
        show_cmds.conf_dev_type(connection, cisco_device, ios12config_file, ios15config_file, iosxeconfig_file, nxosconfig_file)
        
    
        # 5. Send show commands to check2
        print("\nGetting AAA & TACACS")
        show_tacacs, removal_conf = show_cmds.get_tacacs(connection, dev_details)

        show_tacacs_dict = {"IP Address":host_ip, 
                        "Hostname":hostname, 
                        "Username":host_username, 
                        "Current Config":show_tacacs}      
        configured_list.append(show_tacacs_dict)


        # 6. Close Connection
        check_tacacs_cmds_iosxe.close_connection(connection)
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
        with open (f"{basedir}/iosxe_TACACS_Config_Failure_IPs.txt", "a") as f:
            f.write(ip + "\n")

# Write Output
write_file = f"{basedir}/iosxe_tacacs_config.csv"
check_tacacs_csv.write_csv(write_file,configured_list)

