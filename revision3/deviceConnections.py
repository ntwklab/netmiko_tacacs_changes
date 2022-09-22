from netmiko import ConnectHandler


class BaseConn():
    
    def __init__(self):
        pass

    def open_connection(self,cisco_device):
        connection = ConnectHandler(**cisco_device)

        # Get device hostname & IP
        prompt = connection.find_prompt()
        hostname = prompt[0:-1]
        host_ip = cisco_device["host"]
        host_username = cisco_device["username"]
        host_password = cisco_device["password"]
        

        # Enable Mode Check
        prompt = connection.find_prompt()
        if ">" in prompt:
            print("Entering the enable mode ...")
            connection.enable()
        
        return connection, hostname, host_ip, host_username, host_password


    def close_connection(self,connection):
        # Closing the connection
        connection.disconnect()
        


    def get_version(self, connection):
        show_version = BaseConn.send_commands(self, connection, "show version", True)
        show_inventory = BaseConn.send_commands(self, connection,"show inventory", True)
        version = show_version[0]["version"].split(".")[0]
        inventory = show_inventory[0]["descr"].split(" ")[0]

        if version == "12":
            device_version = "ios12"
        elif version == "15":
            device_version = "ios15"
        elif  " 16" in version:
            device_version = "iosxe"
        elif "NX-OS" in inventory:
            device_version = "nxos"
        elif "Nexus" in inventory:
            device_version = "nxos"
        else:
            device_version = "unknown"

        return device_version


    def send_commands(self,connection, command, use_textfsm):
        show_tacacs = connection.send_command(command, use_textfsm=use_textfsm)     
        return show_tacacs


    def send_config_file(self,connection,config_file):
        """
        First check to see if the commands being passed in are
         a file or a list of commands ready to go.
        Then send the commands as a list to the device.
        """

        if type(config_file) == list:
            config_command_list = config_file
        else:
            config_command_list = []
            with open(config_file, "r") as f:
                config_command_list = f.read().splitlines()

        # Enter conf t
        if not connection.check_config_mode():
            connection.config_mode()
        
        # Send commands
        connection.send_config_set(config_command_list)
        

class CmdLibrary():

    def __init__(self):
        pass

    def get_tacacs(self, connection, dev_details):

        if dev_details["Device Version"] != "nxos":
            show_tacacs = BaseConn.send_commands(self, connection, "sh run | i tacacs|aaa", False)
            show_tacacs_list = []
            if show_tacacs == "":
                # show_tacacs = False
                show_tacacs_list.append("#Nothing to do")
                removal_conf = "\n".join(show_tacacs_list)
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
                    elif "session-id" in line:
                        continue
                    elif "config-commands" in line:
                        continue
                    elif line == "":
                        continue
                    elif "aaa accounting system" in line:
                        show_tacacs_list.append("no aaa accounting system default")
                    else:
                        show_tacacs_list.append("no " + line)
                if show_tacacs_list == []:
                    show_tacacs_list.append("#Nothing to do")
                removal_conf = "\n".join(show_tacacs_list)


        elif  dev_details["Device Version"] == "nxos":
            show_tacacs = BaseConn.send_commands(self, connection, "sh run | i tacacs|aaa", False)
            show_tacacs_list = []
            if show_tacacs == "":
                # show_tacacs = False
                show_tacacs_list.append("#Nothing to do")
                removal_conf = "\n".join(show_tacacs_list)
            else:
                output_list = show_tacacs.splitlines()
                for line in output_list:
                    if "feature " in line:
                        continue
                    else:
                        show_tacacs_list.append("no " + line)
                if show_tacacs_list == []:
                    show_tacacs_list.append("#Nothing to do")
                removal_conf = "\n".join(show_tacacs_list)                  

        return show_tacacs, removal_conf
    

    def conf_dev_type(self, connection, cisco_device, ios12config_file, ios15config_file, iosxeconfig_file, nxosconfig_file):

        if cisco_device["Device_Version"] == "ios12":
            config_file = ios12config_file
        elif cisco_device["Device_Version"] == "ios15":
            config_file = ios15config_file
        elif cisco_device["Device_Version"] == "iosxe":
            config_file = iosxeconfig_file
        elif cisco_device["Device_Version"] == "nxos":
            config_file = nxosconfig_file
        else:
            print("unknown OS Type")
        
        BaseConn.send_config_file(self, connection, config_file)
