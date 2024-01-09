#################################################################################
#  *********************  Remote_Server_Control_App.py  *********************** #
#                                                                               #
#   This module is installed on the Remote Administrator's computer.            #
#   It is the main program for the remote server control application.           #
#                                                                               #
#  Function:                                                                    #
#    1. Server Control GUI                                                      #
#    2. Connect to server, execute commands                                     #
#    3. Get various server Infos (CPU info, OS info)                            #
#    4. Remote Desktop Control  (xfreerdp)                                      #
#    5. Start/Stop server remotely                                              #
#                                                                               #
#  @author Houssem Abdellatif                                                   #
#  @version 3.0 , 20/12/23                                                      #
#################################################################################


import subprocess
import tkinter as tk
from tkinter import ttk
from server_configuration import SERVER_CONFIGS
import paramiko


class ButtonTree(ttk.Frame):
    def __init__(self, parent, items):
        ttk.Frame.__init__(self, parent, borderwidth=10, relief="groove")
        self.parent = parent
        self.items = items
        self.master.title("BHT Remote Server Control")

        tree_style = ttk.Style()
        tree_style.configure("Custom.Treeview")
        self.style = ttk.Style()
        self.style.configure("TButton", foreground="black", background="teal")
        self.style.configure("TFrame", foreground="teal")

        self.tree = MyTree(self, items)
        self.tree.grid(column=0, row=0, sticky=tk.N)

        num_visible_rows = 3
        self.tree["height"] = num_visible_rows

        self.buttons = ttk.Frame(self, width=450)
        self.buttons.grid(column=1, row=0, sticky=tk.N )
        add_server_button = ttk.Button(self.buttons, text="Add Server", command=self.openAddserverWindow)
        add_server_button.place(in_=self.buttons, x=0, y=0, width=80)
        print(self.tree.config())

    def handle_add_server(self, tkSubInstance, entry_vars):
        tkSubInstance.destroy()
        new_server = {}
        for index, var in enumerate(entry_vars):
            if index == 0:
                new_server["servername"] = var.get()
            if index == 1:
                new_server["hostname"] = var.get()
            if index == 2:
                new_server["username"] = var.get()
            if index == 3:
                new_server["password"] = var.get()
            if index == 4:
                new_server["ipmi_address"] = var.get()
            if index == 5:
                new_server["ipmi_username"] = var.get()
            if index == 6:
                new_server["ipmi_password"] = var.get()
        print(new_server)
        new_server["id"] = len(server_configs) + 1
        server_configs.append(new_server)
        self.refresh_ui()

    def openAddserverWindow(self):
        tkSubInstance = tk.Toplevel()
        tkSubInstance.title("Toplevel")

        field_labels = ["Enter servername:", "Enter hostname:", "Enter username:", "Enter password:", "Enter ipmi_address:", "Enter ipmi_username:", "Enter ipmi_password:"]
        entry_vars = [tk.StringVar() for _ in range(len(field_labels))]
        entries = [tk.Entry(tkSubInstance, textvariable=var, width=30) for var in entry_vars]

        for row, (label, entry) in enumerate(zip(field_labels, entries)):
            label_widget = tk.Label(tkSubInstance, text=label)
            label_widget.grid(row=row, column=0, sticky="e", padx=10)
            entry.grid(row=row, column=1, padx=10, pady=5)


        submit_button = tk.Button(tkSubInstance, text="Submit", command=lambda: self.handle_add_server(tkSubInstance, entry_vars))
        submit_button.grid(row=len(field_labels), columnspan=2, pady=10)

    def handle_remove_server(self, server_config):
        global server_configs
        server_configs = [item for item in server_configs if item.get("id") != server_config["id"]]
        self.refresh_ui()
        connect_buttons.pop()["connect_button"].destroy()
        stop_buttons.pop()["stop_button"].destroy()
        start_buttons.pop()["start_button"].destroy()
        remove_buttons.pop()["remove_button"].destroy()
        RDC_buttons.pop()["rdc_button"].destroy()


    def handle_connect_click(self, item):
        print(f"Connecting to : {item}")
        self.connect_to_server(item)
        self.get_os_info(item)
        self.get_cpu_info(item)
        self.refresh_ui()

    def handle_rdc_click(self, item):
        print(f"RDC TO START ON {item}")
        self.start_remote_desktop(item)
        self.refresh_ui()

    def handle_start_click(self, item):
        print(f"Starting server: {item['hostname']}")
        self.start_server_with_ipmi(item)
        self.refresh_ui()

    def handle_stop_click(self, item):
        print(f"Stopping server : {item['hostname']}")
        self.stop_server_with_ipmi(item)
        self.refresh_ui()

    def refresh_ui(self):
        h = 20
        self.tree.delete(*self.tree.get_children())
        total_height = sum(self.tree.bbox(item)[3] - self.tree.bbox(item)[1] for item in self.tree.get_children()) + 2
        print(self.tree.winfo_height())
        print(total_height)

        self.tree.configure(height=len(server_configs))
        for server in server_configs:
            server_id = server["id"]
            server_name = server["servername"]
            self.tree.insert(parent="", iid=server_id, text=f"{server_name}", values=server["hostname"], index="end")
        for server_hostname, server_info in servers_infos.items():
            server_id = server_info["id"]
            self.tree.item(server_id, values=(server_hostname, server_info["cpu_infos"], server_info["os_infos"]))

        #process
        if len(server_configs) > len(connect_buttons):
            header_height = 33
            so_far = 33 + 20 * (len(server_configs) - 1)
            last_server = server_configs[len(server_configs) - 1]
            connect_button = ttk.Button(self.buttons, text="Connect",command=lambda last_server=last_server: self.handle_connect_click(last_server))
            rdc_button = ttk.Button(self.buttons, text="Remote Desk.", command=lambda last_server=last_server: self.handle_rdc_click(last_server))
            start_button = self.create_rounded_button(root, last_server, so_far, 20)
            stop_button = self.create_rounded_button_stop(root, last_server, so_far, 20)
            remove_button = ttk.Button(self.buttons, text="Remove", command=lambda last_server=last_server: self.handle_remove_server(last_server))
            connect_button.place(in_=self.buttons, x=0, y=so_far, width=80, height=20)
            rdc_button.place(in_=self.buttons, x=85, y=so_far, width=110, height=20)
            remove_button.place(in_=self.buttons, x=270, y=so_far, width=110, height=20)
            self.buttons["height"] = len(server_configs) * 30 + header_height
            server_cb = {"serverId": last_server["id"], "connect_button": connect_button}
            server_rdcb = {"serverId": last_server["id"], "rdc_button": rdc_button}
            server_sb = {"serverId": last_server["id"], "start_button": start_button}
            server_stop_b = {"serverId": last_server["id"], "stop_button": stop_button}
            server_rb = {"serverId": last_server["id"], "remove_button": remove_button}
            connect_buttons.append(server_cb)
            RDC_buttons.append(server_rdcb)
            start_buttons.append(server_sb)
            stop_buttons.append(server_stop_b)
            remove_buttons.append(server_rb)

    def create_buttons(self):
        self.update()
        so_far = header_height = 33

        for item_name, item in zip(self.tree.get_children(), self.items):
            h = self.tree.bbox(item_name)[-1]

            print(item_name)

            connect_button = ttk.Button(self.buttons, text="Connect", command=lambda item=item: self.handle_connect_click(item))
            rdc_button = ttk.Button(self.buttons, text="Remote Desk.", command=lambda item=item: self.handle_rdc_click(item))
            remove_button = ttk.Button(self.buttons, text="Remove", command=lambda item=item: self.handle_remove_server(item))
            start_button = self.create_rounded_button(root, item, so_far, h)
            stop_button = self.create_rounded_button_stop(root, item, so_far, h)
            connect_button.place(in_=self.buttons, x=0, y=so_far, width=80, height=h)
            rdc_button.place(in_=self.buttons, x=85, y=so_far, width=110, height=h)
            remove_button.place(in_=self.buttons, x=270, y=so_far, width=110, height=h)

            so_far += h
            header_height = h

            server_cb = {"serverId": item["id"], "connect_button": connect_button}
            server_rdcb = {"serverId": item["id"], "rdc_button": rdc_button}
            server_sb = {"serverId": item["id"], "start_button": start_button}
            server_stop_b = {"serverId": item["id"], "stop_button": stop_button}
            server_rb = {"serverId": item["id"], "remove_button": remove_button}

            connect_buttons.append(server_cb)
            RDC_buttons.append(server_rdcb)
            start_buttons.append(server_sb)
            stop_buttons.append(server_stop_b)
            remove_buttons.append(server_rb)

        self.buttons["height"] = len(self.items) * 30 + header_height

    def create_rounded_button(self, parent, item, so_far, h):
        button_width = 30
        button_height = 15
        font_size = 8
        button_canvas = tk.Canvas(parent, width=button_width, height=button_height, highlightthickness=0)
        button_canvas.pack(side=tk.TOP, padx=5, pady=1)

        button_canvas.create_oval(0, 0, button_width, button_height, fill="DarkOliveGreen4")
        button_canvas.create_text(button_width / 2, button_height / 2, text="Start", fill="black", font=("DarkOliveGreen4", font_size, "bold"))

        button_canvas.bind("<Button-1>", lambda event, config=item: self.start_server_with_ipmi(item))
        button_canvas.place(in_=self.buttons, x=205, y=so_far+2, height=h)
        return button_canvas

    def create_rounded_button_stop(self, parent, item, so_far, h):
        button_width = 30
        button_height = 15
        font_size = 8
        button_canvas_stop = tk.Canvas(parent, width=button_width, height=button_height, highlightthickness=0)
        button_canvas_stop.pack(side=tk.TOP, padx=5, pady=1)

        button_canvas_stop.create_oval(0, 0, button_width, button_height, fill="red")
        button_canvas_stop.create_text(button_width / 2, button_height / 2, text="Stop", fill="black", font=("black", font_size, "bold"))

        button_canvas_stop.bind("<Button-1>", lambda event, config=item: self.stop_server_with_ipmi(item))
        button_canvas_stop.place(in_=self.buttons, x=240, y=so_far+2, height=h)
        return button_canvas_stop


    def execute_ssh_command(self, command, server_config):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(server_config["hostname"], username=server_config["username"],
                           password=server_config["password"])

            stdin, stdout, stderr = client.exec_command(command)

            output = stdout.read().decode()
            client.close()
            return output
        except Exception as e:
            error_message = f"Error: {e}"
            return error_message

    def start_server_with_ipmi(self, config):
        server_config = config
        # IPMI command to start the server
        ipmi_command = f"ipmitool -I lanplus -H {server_config['ipmi_address']} -U {server_config['ipmi_username']} -P {server_config['ipmi_password']} power on"

        try:
            subprocess.run(ipmi_command, shell=True, check=True)
            print("Server started successfully using IPMI.")
        except subprocess.CalledProcessError as e:
            error_message = f"Error: {e}"
            print(f"Failed to start the server using IPMI. {error_message}")
    def stop_server_with_ipmi(self, config):
        server_config = config
        # Construct the IPMI command to start the server
        ipmi_command = f"ipmitool -I lanplus -H {server_config['ipmi_address']} -U {server_config['ipmi_username']} -P {server_config['ipmi_password']} power off"


        try:
            subprocess.run(ipmi_command, shell=True, check=True)
            print("Server Shutdown successfully using IPMI.")
        except subprocess.CalledProcessError as e:
            error_message = f"Error: {e}"
            print(f"Failed to shutdown the server using IPMI. {error_message}")


    def connect_to_server(self, config):
        selected_server = config["hostname"]
        print("Connecting")

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(config["hostname"], username=config["username"], password=config["password"])

            client.close()
        except Exception as e:
            print(f"ERROR {selected_server}.")
            error_message = f"Error connecting to {selected_server}: {e}"


    def get_cpu_info(self, config):

        server_config = config

        command = "cat /proc/cpuinfo | grep 'model name' | uniq"
        command_output = self.execute_ssh_command(command, server_config)
        if not server_config["hostname"] in servers_infos:
            servers_infos[server_config["hostname"]] = {}
        servers_infos[server_config["hostname"]]["cpu_infos"] = command_output
        servers_infos[server_config["hostname"]]["id"] = config["id"]

    def get_os_info(self, config):
        server_config = config

        command = "uname -a"
        command_output = self.execute_ssh_command(command, server_config)
        if not server_config["hostname"] in servers_infos:
            servers_infos[server_config["hostname"]] = {}
        servers_infos[server_config["hostname"]]["os_infos"] = command_output




    def execute_command_in_output(self, command, output_text_widget, config):
        server_config = config

        command_output = self.execute_ssh_command(command, server_config)
        output_text_widget.config(state="normal")
        output_text_widget.insert(tk.END, f"$ {command}\n{command_output}\n")
        output_text_widget.config(state="disabled")

    def start_remote_desktop(self, config):
        server_config = config

        try:
            # xfreerdp to connect to the Linux server's desktop via RDP
            rdp_command = f"xfreerdp /v:{server_config['hostname']}"

            # subprocess to run the xfreerdp command
            subprocess.run(rdp_command, shell=True)
        except Exception as e:
            error_message = f"Error starting remote desktop: {e}"


class MyTree(ttk.Treeview):
    def __init__(self, parent, servers):
        ttk.Treeview.__init__(self, parent, columns=("server_ip", "cpu_info", "os_info"), padding=10)
        self.heading("#0", text="Server Name")
        self.heading("server_ip", text="Server IP ")
        self.heading("cpu_info", text="CPU Info")
        self.heading("os_info", text="OS Info")


        # Set the width of the columns
        self.column("#0", width=80, anchor="center")
        self.column("server_ip", width=150, anchor="center")
        self.column("cpu_info", width=350, anchor="w")
        self.column("os_info", width=350, anchor="w")


        self.servers = servers
        for server in self.servers:
            server_id = server["id"]
            server_name = server["servername"]
            self.insert(parent="", iid=server_id, text=f"{server_name}", values=server["hostname"], index="end")


if __name__ == "__main__":
    root = tk.Tk()
    connect_buttons = []
    RDC_buttons = []
    start_buttons = []
    stop_buttons = []
    remove_buttons = []
    servers_infos = {}
    server_configs = SERVER_CONFIGS
    buttonTree = ButtonTree(root, server_configs)
    root.iconbitmap(r"C:\Users\abdel\Downloads\rsz_bht_logo_horizontal_anthrazit_rgb_144ppi.ico")
    buttonTree.pack(padx=10, pady=10)
    buttonTree.create_buttons()
    root.mainloop()