import tkinter as tk
from tkinter import ttk
from timeit import default_timer as timer
from dateutil import parser
import threading
import datetime
import socket
import time
import subprocess
from time import strftime

stop_flag = False


def get_ip():
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


# client thread function used to send time at client side
def startSendingTime(slave_client):
    while not stop_flag:
        # provide server with clock time at the client
        slave_client.send(str(
            datetime.datetime.now()).encode())

        print("Recent time sent successfully",
              end="\n\n")
        time.sleep(5)


def cmdTimeSync(command):
    try:
        subprocess.run(["powershell", "-Command", f"Start-Process cmd -ArgumentList '/c {command}' -Verb RunAs"],
                       check=True)
    except subprocess.CalledProcessError:
        print("Failed to run the command with admin privileges.")


# client thread function used to receive synchronized time
def startReceivingTime(slave_client):
    while not stop_flag:
        # receive data from the server
        Synchronized_time = parser.parse(
            slave_client.recv(1024).decode())

        print("Synchronized time at the client is: " + str(Synchronized_time),
              end="\n\n")
        time_part = str(Synchronized_time)[11:19]
        command = "time " + time_part

        cmdTimeSync(command)


# function used to Synchronize client process time
def initiateSlaveClient(port, server_ip, connection_type):
    if connection_type == "TCP":
        slave_client = socket.socket()
    elif connection_type == "UDP":
        slave_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # connect to the clock server on local computer 
    slave_client.connect((server_ip, port))

    # start sending time to server 
    print("Starting to receive time from server\n")
    send_time_thread = threading.Thread(
        target=startSendingTime,
        args=(slave_client,))
    send_time_thread.start()

    # start receiving synchronized from server
    print("Starting to receiving " + \
          "synchronized time from server\n")
    receive_time_thread = threading.Thread(
        target=startReceivingTime,
        args=(slave_client,))
    receive_time_thread.start()


def start():
    global stop_flag
    # server_name = get_ip_server()
    server_ip = server_IP_entry.get()
    client_port = int(client_port_entry.get())
    connection_type = connection_type_var.get()

    stop_flag = False

    # Gọi hàm khởi động server với thông tin đã nhập

    initiateSlaveClient(port=client_port, server_ip=server_ip, connection_type=connection_type)


def end():
    print("stop server")
    global stop_flag
    stop_flag = True


def timenow():
    string = strftime('%H:%M:%S %p')
    lbl.config(text=string)
    lbl.after(1000, timenow)


# Tạo cửa sổ chính
root = tk.Tk()
frm = ttk.Frame(root)
root.geometry("500x400")

root.title("Client")
# client address
client_IP_label = tk.Label(root, text="Your IP:", background="#E5E8E8")
client_IP_label.place(x=120, y=30)
client_IP = tk.Label(root, text=get_ip(), background="WHITE")
client_IP.place(x=240, y=30)

# server address
server_IP_label = tk.Label(root, text="IP Server:", background="#E5E8E8")
server_IP_label.place(x=120, y=70)
server_IP_entry = tk.Entry(root, background="WHITE")
server_IP_entry.place(x=240, y=70)

# Port client
client_port_label = tk.Label(root, text="Port:", background="#E5E8E8")
client_port_label.place(x=120, y=110)
client_port_entry = tk.Entry(root)
client_port_entry.place(x=240, y=110)

# Tùy chọn kết nối (TCP/UDP)
connection_type_label = tk.Label(root, text="Connection Type:", bg="#E5E8E8")
connection_type_label.place(x=120, y=150)

# Sử dụng Radiobutton
connection_type_var = tk.StringVar(value="TCP")
tcp_button = tk.Radiobutton(root, text="TCP", variable=connection_type_var, value="TCP")
tcp_button.place(x=240, y=150)
udp_button = tk.Radiobutton(root, text="UDP", variable=connection_type_var, value="UDP")
udp_button.place(x=240, y=170)

# Nút bắt đầu kết nối
start_button = tk.Button(root, text="Start Connect", background="#FA8072", command=start)
start_button.place(x=120, y=210)

# Nút stop  
e_button = tk.Button(root, text="Stop connect ", background="#FA8072", command=end)
e_button.place(x=280, y=210)

#Exit chương trình, dừng chạy
exit_buton = ttk.Button(root, text="Exit", command=root.destroy).place(x=400, y=360)

# Clock

lbl = tk.Label(root, font=('calibri', 20, 'bold'),
               background='red',
               foreground='white')
lbl.place(x=180, y=270)

# Main loop
timenow()
root.mainloop()


