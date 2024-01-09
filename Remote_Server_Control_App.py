#################################################################################
#  *********************  Remote_Server_Control_App.py  *********************** #
#                                                                               #
#   This module is installed on the Remote Administrator's computer.            #
#   It is the main program for the remote server control application.           #
#                                                                               #
#  Function:                                                                    #
#    1. Server Control GUI                                                      #
#    2. Connect to server, execute commands.                                    #
#                                                                               #
#
#  @author Houssem Abdellatif                                                   #
#  @version 1.0 , 02/12/23                                                      #
#################################################################################

import paramiko
import tkinter as tk
from tkinter import ttk
from server_configs import SERVER_CONFIGS  # Import the server configurations

class ServerControlApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Server Control")
        self.server_configs = SERVER_CONFIGS
        self.create_widgets()


    def create_widgets(self):
        self.server_label = ttk.Label(self.master, text="Select Server:")
        self.server_label.grid(row=0, column=0, padx=10, pady=10)

        self.server_var = tk.StringVar()
        self.server_dropdown = ttk.Combobox(self.master, textvariable=self.server_var, state="readonly")
        self.server_dropdown["values"] = [config["hostname"] for config in self.server_configs]
        self.server_dropdown.grid(row=0, column=1, padx=10, pady=10)

        self.command_label = ttk.Label(self.master, text="Enter Command:")
        self.command_label.grid(row=1, column=0, padx=10, pady=10)

        self.command_entry = ttk.Entry(self.master)
        self.command_entry.grid(row=1, column=1, padx=10, pady=10)

        self.execute_button = ttk.Button(self.master, text="Execute Command", command=self.execute_command)
        self.execute_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.output_text = tk.Text(self.master, height=10, width=50, state="disabled")
        self.output_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def execute_command(self):
        selected_server = self.server_var.get()

        server_config = next(config for config in self.server_configs if config["hostname"] == selected_server)

        command = self.command_entry.get()

        try:
            # Create an SSH client
            client = paramiko.SSHClient()
            # Automatically add the server's host key
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Connect to the server
            client.connect(server_config["hostname"], username=server_config["username"],password=server_config["password"])

            # Execute the command
            stdin, stdout, stderr = client.exec_command(command)

            # Display the output in the text widget
            output = stdout.read().decode()
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, output)
            self.output_text.config(state="disabled")

            # Close the SSH connection
            client.close()
        except Exception as e:
            error_message = f"Error: {e}"
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, error_message)
            self.output_text.config(state="disabled")


def main():
    root = tk.Tk()
    app = ServerControlApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
