# from netmiko import ConnectHandler
import csv
import pandas as pd
import os
from dotenv import load_dotenv


class csv_devices():

    def __init__(self):
        pass
        

    def open_csv(self, open_file):
        # Create a dataframe from csv
        df = pd.read_csv(open_file, delimiter=',')
        # Create a list of tuples for Dataframe rows using list comprehension
        csv_data = [tuple(row) for row in df.values]
        return csv_data
        
    
    def write_csv(self,write_file, success_list):

        # Output
        with open(write_file, "w", newline="") as f:
            csv_writer = csv.DictWriter(f, success_list[0].keys())
            csv_writer.writeheader()
            csv_writer.writerows(success_list)
        print("CSV written out")


    def create_device_list(self,csv_data):
        i = 0
        device_list = list()
        ip_list = list()
        for device in csv_data:
            ip,hostname,username = csv_data[i]

            # Load the .env file
            load_dotenv()
            # Assign corerct password for username
            if username == "admin":
                user_pass = os.getenv("ADMIN_DEVICE_PASSWORD")
            elif username == "cisco":
                user_pass = os.getenv("CISCO_DEVICE_PASSWORD") 
            else:
                user_pass = os.getenv("TACACS_DEVICE_PASSWORD")

            # Iterating over the list with the devices ip addresses
            cisco_device = {
                "device_type": "cisco_ios",
                "host": ip,
                "username": username,
                "password": user_pass,
                "port": 22,
                "secret": os.getenv("ENABLE_DEVICE_PASSWORD"),
                "verbose": True
                }
            device_list.append(cisco_device)
            ip_list.append(ip)
            # Add 1 to i for the next device
            i += 1
        return device_list,ip_list


    # Create list of IPs
    def ip_list(self,ips_list):
        # Devices Connecting to...
        print("\nThese are the devices that we will be connecting to...")
        for ip in ips_list:
            print(f"IP Address: {ip}")
        print("\n")

