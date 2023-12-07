import paramiko
import sys
import time

def print_config_commands(interface, descr, subnet):
    print(f'int {interface}')
    print(f'desc {descr}')
    print(f'switchport access vlan {subnet}')

def config_open_ports():
    subnet = 1
    descr = "OPEN"
    range_input = input("Input the range of ports separated by a space (One switch at a time). If necessary, follow with even or odd:\n")
    print("\n")
    port1, port2, parity = map(str, range_input.split())
    sw_num = port1[2]

    print("config t")

    sw_port1, sw_port2 = int(port1[2]), int(port2[2])
    iterates = sw_port2 - sw_port1

    for i in range(iterates + 1):
        if sw_port1 % 2 == 0 and parity != "odd":
            print_config_commands(f'Gi{sw_num}/0/{sw_port1}', descr, subnet)
        elif sw_port1 % 2 == 1 and parity != "even":
            print_config_commands(f'Gi{sw_num}/0/{sw_port1}', descr, subnet)
        sw_port1 += 1

    print("end")
    print("write mem")

def config_list_ports():
    subnet = 1
    descr = "OPEN"
    port_list = []

    print("\n")
    port_info = input("Port: ")
    
    while port_info != "-1":
        port_list.append(port_info)
        port_info = input("Port: ")
    
    print("\n\n")
    print("config t")

    for port in port_list:
        print_config_commands(port[:8], descr, subnet)

    print("end")
    print("write mem")
    print("\n\n")

def reorder_ports():
    port_list = []

    port_input = input("Input a list of ports, then -1:\n")
    
    while port_input != "-1":
        port_list.append(port_input)
        port_input = input("Input a list of ports, then -1:\n")
    
    for i in range(len(port_list)):
        descs = port_list[i][13:23].split("-")
        descs[1], descs[2] = descs[2].strip(" "), descs[1].strip(" ")
        print_config_commands(port_list[i][:8], "desc "+descs[0]+"-"+descs[1]+"-"+descs[2], 1)

def rename_ports():
    descs = []
    port_list = []
    ap_ports = []
    power_list = []
    ap_port_list = []

    building = input("Enter the building code:")
    power_inline = input("Input the power inline from the switch, then -1: ")
    
    while power_inline != "-1":
        power_list.append(power_inline)
        power_inline = input("Input the power info, then -1:\n")
    
    for i in range(len(power_list)):
        if power_list[i][36:46] == "C9105AXW-B":
            ap_port_list.append(power_list[i][:8])
    
    port_input = input("Input a list of ports, then -1:\n")
    
    while port_input != "-1":
        for j in range(len(ap_port_list)):
            if port_input[:8] == ap_port_list[j]:
                port_list.append(port_input)
            else:
                pass
        port_input = input("Input a list of ports, then -1:\n")
    
    for i in range(len(port_list)):
        if port_list[i][23] == "(" or port_list[i][22] == "(":
            descs.append(port_list[i][10:23].split("-"))
        else:
            descs.append(port_list[i][10:28].split("-"))
    
    for j in range(len(descs)):
        room_x = descs[j][2].strip().partition(" ")
        print_config_commands(port_list[j][:8], f'desc {descs[j][0]}-{descs[j][1]}-{room_x[0]} [{building}-0{room_x[0]}-W1] {(room_x[2])}', 1)

def cdp_ports():
    port_list = []
    cdp_neigh = []
    ap_ports = []
    descs = []
    ap_port_list = []
    cdp_ints = []
    building = input("Enter the building code:")

    cdp_input = input("Input the cdp neighbors from the switch, then -1: ")
    
    while cdp_input != "-1":
        cdp_neigh.append(cdp_input.split(" ")[0])
        cdp_ints.append(cdp_input.split(" ")[2])
        cdp_input = input("Input the CDP neigh info, then -1:\n")
    
    port_input = input("Input a list of ports, then -1:\n")
    
    while port_input != "-1":
        for j in range(len(cdp_ints)):
            if port_input[2:9] == cdp_ints[j][2:9]:
                port_list.append(port_input)
            else:
                pass
        port_input = input("Input a list of ports, then -1:\n")
    
    for i in range(len(port_list)):
        if port_list[i][23] == "(" or port_list[i][22] == "(":
            descs.append(port_list[i][10:23].split("-"))
        else:
            descs.append(port_list[i][10:28].split("-"))
    
    for j in range(len(descs)):
        room_x = descs[j][2].strip().partition(" ")
        print_config_commands(port_list[j][:8], f'desc {descs[j][0]}-{descs[j][1]}-{room_x[0]} [{cdp_neigh[j]}]', 1)
    
    print(port_list)
    print(cdp_ints)

def ssh_switch(ip, username, password):
    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to switch
    try:
        ssh.connect(ip, username=username, password=password, timeout=10)
        print(f"Connected to {ip} successfully!")
        # Send command and receive output
        shell = ssh.invoke_shell()
        shell.setblocking(True)
        print("Shell opened")
        time.sleep(2)
        shell.send("term len 0\n")
    except Exception as e:
        print(f"Failed to connect to {ip}: {e}")

    action = input("What would you like to do?")
    if action.lower() == "enable":
        shell.send('en\n')
        shell.send(input("RSA: ") + "\n")
        action = input("What would you like to do?")
        
    if action.lower() == "diagnostic":
        shell.send("show version\n")
        time.sleep(2)
        output = shell.recv(65535).decode("utf-8")
        print(output)
        shell.send("show interfaces status\n")
        time.sleep(2)
        output = shell.recv(65535).decode("utf-8")
        print(output)

    if action.lower() == "custom":
        commands = []
        entry = input("Input a command: ")
        while entry != "-1":
            commands.append(entry)
            entry = input("Input a command, or -1 to stop: ")
        for command in commands:
            shell.send(command + '\n')
            time.sleep(2)
            output = shell.recv(65535).decode("utf-8")
            print(output)

    # Close SSH connection
    ssh.close()

def main():
    args = sys.argv[1:]

    if len(args) == 0 or args[0] == "-h" or args[0] == "--help":
        print("This program will create commands that can be entered directly into the Cisco config terminal. You can enter the following:\n\nConfig - Set a large number of ports to OPEN by inputting a range or raw list of ports.\nReorder - Fix orders of descriptions\nRename - Adjust AP names to new standard (1/10/2023)\nDescription Fix\nSSH\n\n\nExample of how to run: python config.py config\n")
    elif args[0] == "config":
        path = input("Would you like to input a range or list of ports? (list, range):\n")
        if path == "range":
            config_open_ports()
        elif path == "list":
            config_list_ports()
    elif args[0] == "reorder":
        reorder_ports()
    elif args[0] == "rename":
        rename_ports()
    elif args[0] == "cdp":
        cdp_ports()
    elif args[0] == "ssh":
        ip = input("Enter an IP:")
        username = 'oit-edenbo'
        password = input("Input RSA token:")
        ssh_switch(ip, username, password)
    else:
        print("Invalid Input. Please try again.")

if __name__ == "__main__":
    main()
