import tkinter as tk
from tkinter import ttk
import threading
from dateutil import parser
import datetime
import socket
import time
from time import strftime
import sys
# Data structure used to store client address and clock data
client_data = {}

stop_flag = False
import socket
def get_ip_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def startReceivingClockTimeTCP(connector, address):
    print("Vo TCPPPPPPPPPP")
    while not stop_flag:
        try:
            # Receive clock time
            clock_time_string = connector.recv(1024).decode()
            if not clock_time_string:
                # Kết nối đã đóng
                break
            clock_time = parser.parse(clock_time_string)
            clock_time_diff =  clock_time - datetime.datetime.now()

            client_data[address] = {
                "clock_time": clock_time,
                "time_difference": clock_time_diff,
                "connector": connector
            }

            print("Client Data updated with: " + str(address), end="\n\n")
            time.sleep(5)
        except Exception as e:
            print("Error receiving clock time from " + str(address) + ": " + str(e))


def startReceivingClockTimeUDP(master_server):
    print("vo UDPPPPPPPPPPPPPPP")
    while not stop_flag:
        try:
            # Receive clock time and client address from UDP
            data, addr = master_server.recvfrom(1024)
            if not data:
                break
            clock_time_string = data.decode()
            clock_time = parser.parse(clock_time_string)
            clock_time_diff = datetime.datetime.now() - clock_time

            slave_address = str(addr[0]) + ":" + str(addr[1])

            client_data[slave_address] = {
                "clock_time": clock_time,
                "time_difference": clock_time_diff,
                "connector": master_server
            }

            print("Client Data updated with: " + slave_address, end="\n\n")
            time.sleep(5)
        except Exception as e:
            print("Error receiving clock time from " + slave_address + ": " + str(e))
            client_data.pop(slave_address)

# def startReceivingClockTime(connector, address, connection_type):
#     global stop_flag
#     while not stop_flag:
#         try:
#             # Receive clock time
#             if connection_type == "TCP":
#                 clock_time_string = connector.recv(1024).decode()
#                 clock_time = parser.parse(clock_time_string)
#                 clock_time_diff =  clock_time - datetime.datetime.now()
            
#             elif connection_type == "UDP":
#                 data, addr = connector.recvfrom(1024)
#                 clock_time_string = data.decode()
#                 clock_time = parser.parse(clock_time_string)
#                 clock_time_diff = clock_time - datetime.datetime.now()
#                 address = str(addr[0]) + ":" + str(addr[1])
#             client_data[address] = {
#                 "clock_time": clock_time,
#                 "time_difference": clock_time_diff,
#                 "connector": connector
#             }

#             print("Client Data updated with: " + str(address), end="\n\n")
            
#             time.sleep(5)
#         except Exception as e:
#             print("Error receiving clock time from " + str(address) + ": " + str(e))
#             if connection_type=="UDP":
#                 client_data.pop(address)

def startConnecting(master_server, connection_type):
    global stop_flag
    while not stop_flag:
        try:
            # Accepting a client/slave clock client
            if connection_type == 'TCP':
                master_slave_connector, addr = master_server.accept()  # TCP
            elif connection_type == 'UDP':
                data, addr = master_server.recvfrom(1024)  # Receive data and address
            slave_address = str(addr[0]) + ":" + str(addr[1])

            print(slave_address + " got connected successfully")

            if connection_type == "TCP":
                current_thread = threading.Thread(
                    target=startReceivingClockTimeTCP,
                    args=(master_slave_connector, slave_address))
                current_thread.start()
            else:
                current_thread = threading.Thread(
                    target=startReceivingClockTimeUDP,
                    args=(master_server,))
                current_thread.start()
           
        except Exception as e:
            print("Error accepting connection: " + str(e))
    

def getAverageClockDiff():
    current_client_data = client_data.copy()

    time_difference_list = list(client['time_difference']
                                for client_addr, client
                                in client_data.items())

    sum_of_clock_difference = sum(time_difference_list, datetime.timedelta(0, 0))
    average_clock_difference = sum_of_clock_difference / (len(client_data) + 1)

    return average_clock_difference

def synchronizeAllClocks(connection_type):
    global stop_flag
    while not stop_flag:
        print("New synchronization cycle started.")
        print("Number of clients to be synchronized: " + str(len(client_data)))

        if len(client_data) > 0:
            average_clock_difference = getAverageClockDiff()

            for client_addr, client in client_data.items():
                try:
                    synchronized_time = datetime.datetime.now() + average_clock_difference
                    if connection_type=="TCP":
                        client['connector'].send(str(synchronized_time).encode())
                    elif connection_type == "UDP":
                        client['connector'].sendto(str(synchronized_time).encode(), (client_addr.split(':')[0], int(client_addr.split(':')[1])))
                    #Change time on computer
                    time_part = str(Synchronized_time)[11:19]
                    command = "time " + time_part
                    cmdTimeSync(command)
                except Exception as e:
                    print("Error sending synchronized time through " + str(client_addr) + ": " + str(e))
        else:
            print("No client data. Synchronization not applicable.")

        print("\n\n")
        time.sleep(5)
    

def initiateClockServer(port, connection_type):
    if connection_type == 'TCP':
        master_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
    else:
        master_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    master_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("========> " + str(master_server.type))
    print("Socket at master node created successfully\n")

    master_server.bind(('', port))
    if connection_type == 'TCP':
        master_server.listen(10)
    # master_server.listen(10 if connection_type == 'TCP' else 0)
    print("Clock server started...\n")

    # Start making connections
    print("Starting to make connections...\n")
    master_thread = threading.Thread(
        target=startConnecting,
        args=(master_server, connection_type))
    master_thread.start()

    # Start synchronization
    print("Starting synchronization parallelly...\n")
    sync_thread = threading.Thread(
        target=synchronizeAllClocks,
        args=(connection_type))
    sync_thread.start()
    # global stop_flag
    # if not stop_flag:
    #     if connection_type == 'TCP':
    #         master_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
    #     else:
    #         master_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    #     master_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #     print("========> " + str(master_server.type))
    #     print("Socket at master node created successfully\n")

    #     master_server.bind(('', port))
    #     if connection_type == 'TCP':
    #         master_server.listen(10)
    #     # master_server.listen(10 if connection_type == 'TCP' else 0)
    #     print("Clock server started...\n")

    #     # Start making connections
    #     print("Starting to make connections...\n")
    #     master_thread = threading.Thread(
    #         target=startConnecting,
    #         args=(master_server, connection_type))
    #     master_thread.start()

    #         # Start synchronization
    #     print("Starting synchronization parallelly...\n")
    #     sync_thread = threading.Thread(
    #         target=synchronizeAllClocks,
    #         args=())
    #     sync_thread.start()
    # print("Server stopped.")
    # master_server.close()

            










# Function to start the server based on GUI inputs
def start_server():
    global stop_flag
    server_name = get_ip_server()
    server_port = int(server_port_entry.get())
    connection_type = connection_type_var.get()
    
    if server_port == None:
        tk.Message("pop up","Please enter port")

    stop_flag = False

    # Gọi hàm khởi động server với thông tin đã nhập
    # time()
    initiateClockServer(port=server_port, connection_type=connection_type)

def end():
    print("stop server")
    
    global stop_flag
    stop_flag = True
    # sys.exit()

def timenow():
    string = strftime('%H:%M:%S %p')
    lbl.config(text=string)
    lbl.after(1000, timenow)
  
# Tạo cửa sổ chính
root = tk.Tk()
frm = ttk.Frame(root)
root.geometry("500x350")

root.title("Server")
# Tên server
server_name_label = tk.Label(root, text="IP Server:",background= "#E5E8E8")
server_name_label.place(x=120, y=30)
server_IP = tk.Label(root, text=get_ip_server(),background= "WHITE")
server_IP.place(x=240, y= 30)

# Port server
server_port_label = tk.Label(root, text="Port Server:",background="#E5E8E8")
server_port_label.place(x = 120, y = 80)
server_port_entry = tk.Entry(root)
server_port_entry.place(x= 240, y=80)

# Tùy chọn kết nối (TCP/UDP)
connection_type_label = tk.Label(root, text="Connection Type:", bg="#E5E8E8")
connection_type_label.place(x = 120, y=130)

# Sử dụng Radiobutton thay vì Combobox
connection_type_var = tk.StringVar(value="TCP")
tcp_button = tk.Radiobutton(root, text="TCP", variable=connection_type_var, value="TCP")
tcp_button.place(x= 240, y =130)
udp_button = tk.Radiobutton(root, text="UDP", variable=connection_type_var, value="UDP")
udp_button.place(x= 240, y= 150)

# Nút bắt đầu server
start_button = tk.Button(root, text="Start Server",background="#FA8072", command=start_server)
start_button.place(x= 120, y= 180)

# Nút DỪNG  server
e_button = tk.Button(root, text="Stop server ",background="#FA8072", command=end)
e_button.place(x = 280, y = 180 )

exit_buton = ttk.Button(root, text="Exit", command=root.destroy).place(x=410, y = 300)
# exit_buton = ttk.Button(root, text="Exit", command=lambda: sys.exit()).place(x=410, y=300)


#Clock
# Styling the label widget so that clock will look more attractive
lbl = tk.Label(root, font=('calibri', 20, 'bold'),
            background='red',
            foreground='white')
lbl.place(x=180, y=240)
timenow()
# Main loop
root.mainloop()
