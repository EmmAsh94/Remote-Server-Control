#################################################################################
#   *******************Remote_Server_Control_App.py *************************   #
#                                                                               #
#   This module is installed on the Remote Administrator's computer.            #
#   It is the main program for the remote server control application.           #
#                                                                               #
#  Function:                                                                    #
#    1. Server Control GUI                                                      #
#    2. Connect to server, execute commands                                     #
#    3. Get various Server Infos (OS Info, CPU Info, IP)                        #
#                                                                               #
#  @author Houssem Abdellatif                                                   #
#  @version 2.0 , 09/12/23                                                      #
#################################################################################

import paramiko
import tkinter as tk
from tkinter import ttk
import subprocess
from server_configs import SERVER_CONFIGS

class ServerControlApp:
    def __init__(self, master, server_configs):
        self.master = master
        self.master.title("BHT Remote Server Control")

        # Create a style and configure it with the desired color
        self.style = ttk.Style()
        self.style.configure("Teal.TButton", foreground="black", background="#008080")
        self.style.configure("Teal.TFrame", background="#008080")

        self.server_configs = server_configs
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.grid(row=0, column=0)

        # Set the background color of the main frame
        self.main_frame.configure(style="Teal.TFrame")

        self.server_label = ttk.Label(self.main_frame, text="Select Server:")
        self.server_label.grid(row=0, column=0, padx=10, pady=10)


        # Create a title label
        title_label = ttk.Label(self.main_frame, text="Server Control")
        title_label.grid(row=0, column=1, padx=10, pady=10)

        self.connect_button = ttk.Button(self.main_frame, text="Connect to Server", command=self.connect_to_server, style="Teal.TButton")
        self.connect_button.grid(row=0, column=2, pady=10)

        self.server_var = tk.StringVar()
        self.server_dropdown = ttk.Combobox(self.main_frame, textvariable=self.server_var, state="readonly")
        self.server_dropdown["values"] = [config["hostname"] for config in self.server_configs]
        self.server_dropdown.grid(row=0, column=1, padx=10, pady=10)

        self.cpu_info_button = ttk.Button(self.main_frame, text="CPU Info", command=self.get_cpu_info, style="Teal.TButton")
        self.cpu_info_button.grid(row=2, column=0, pady=10)

        self.os_info_button = ttk.Button(self.main_frame, text="OS Info", command=self.get_os_info, style="Teal.TButton")
        self.os_info_button.grid(row=2, column=1, pady=10)

        self.ip_info_button = ttk.Button(self.main_frame, text="IP Address Info", command=self.get_ip_info, style="Teal.TButton")
        self.ip_info_button.grid(row=2, column=2, pady=10)

        self.remote_desktop_button = ttk.Button(self.main_frame, text="Remote Desktop", command=self.start_remote_desktop, style="Teal.TButton")
        self.remote_desktop_button.grid(row=3, column=1, columnspan=2, pady=10)



    def execute_ssh_command(self, command, server_config):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(server_config["hostname"], username=server_config["username"], password=server_config["password"])

            stdin, stdout, stderr = client.exec_command(command)

            output = stdout.read().decode()
            client.close()
            return output
        except Exception as e:
            error_message = f"Error: {e}"
            return error_message

    def connect_to_server(self):
        selected_server = self.server_var.get()
        server_config = next(config for config in self.server_configs if config["hostname"] == selected_server)

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(server_config["hostname"], username=server_config["username"], password=server_config["password"])

            output = f"Successfully connected to {selected_server}."
            self.show_output(output)

            client.close()
        except Exception as e:
            error_message = f"Error connecting to {selected_server}: {e}"
            self.show_output(error_message)

    def get_cpu_info(self):
        selected_server = self.server_var.get()
        server_config = next(config for config in self.server_configs if config["hostname"] == selected_server)

        command = "cat /proc/cpuinfo | grep 'model name' | uniq"
        command_output = self.execute_ssh_command(command, server_config)
        self.show_output(command_output)

    def get_os_info(self):
        selected_server = self.server_var.get()
        server_config = next(config for config in self.server_configs if config["hostname"] == selected_server)

        command = "uname -a"
        command_output = self.execute_ssh_command(command, server_config)
        self.show_output(command_output)

    def get_ip_info(self):
        selected_server = self.server_var.get()
        server_config = next(config for config in self.server_configs if config["hostname"] == selected_server)

        command = "hostname -I"
        command_output = self.execute_ssh_command(command, server_config)
        self.show_output(command_output)

    def show_output(self, message):
        output_window = tk.Toplevel(self.master)
        output_window.title("Terminal Output")

        # Entry widget for typing commands
        command_entry = ttk.Entry(output_window, width=50)
        command_entry.pack(pady=5)

        # Button to execute the command
        execute_button = ttk.Button(output_window, text="Execute Command", command=lambda: self.execute_command_in_output(command_entry.get(), output_text))
        execute_button.pack(pady=5)

        # Text widget for displaying output
        output_text = tk.Text(output_window, height=30, width=80, bg="black", fg="white")
        output_text.insert(tk.END, message)
        output_text.pack()

    def execute_command_in_output(self, command, output_text_widget):
        selected_server = self.server_var.get()
        server_config = next(config for config in self.server_configs if config["hostname"] == selected_server)

        command_output = self.execute_ssh_command(command, server_config)
        output_text_widget.config(state="normal")
        output_text_widget.insert(tk.END, f"$ {command}\n{command_output}\n")
        output_text_widget.config(state="disabled")

    def start_remote_desktop(self):
        selected_server = self.server_var.get()
        server_config = next(config for config in self.server_configs if config["hostname"] == selected_server)

        try:
            # Use xfreerdp to connect to the Linux server's desktop via RDP
            rdp_command = f"xfreerdp /v:{server_config['hostname']}"

            # Use subprocess to run the xfreerdp command
            subprocess.run(rdp_command, shell=True)
        except Exception as e:
            error_message = f"Error starting remote desktop: {e}"
            self.show_output(error_message)


def main():
    server_configs = SERVER_CONFIGS
    root = tk.Tk()

    # Create a style for the main frame
    ttk.Style().configure("Teal.TFrame", background="#008080")
    root.iconbitmap(r"C:\Users\abdel\Downloads\rsz_bht_logo_horizontal_anthrazit_rgb_144ppi.ico")

    app = ServerControlApp(root, server_configs)
    root.mainloop()

if __name__ == "__main__":
    main()
