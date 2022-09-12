from netmiko import ConnectHandler


class ios_xe():
    
    def __init__(self):
        pass

    def open_connection(self,cisco_device):
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
        
        return connection, hostname, host_ip, host_username


    def close_connection(self,connection):
        # Closing the connection
        print("\nClosing connection")
        connection.disconnect()
        print("#" * 30 +"\n")


    def send_commands(self,connection, command):
        
        show_tacacs = connection.send_command(command)     
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

            print("Config file to be applied")
            for line in config_command_list:
                print (line)
            print("\n")

        # Enter conf t
        if not connection.check_config_mode():
            connection.config_mode()
            print("Entering the config mode ...\n")
        
        print("Applying config...")
        connection.send_config_set(config_command_list)
        print("\nConfig Complete...\n")

