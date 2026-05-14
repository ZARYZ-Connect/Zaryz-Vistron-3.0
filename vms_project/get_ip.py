import socket
try:
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"IP: {ip_address}")
except Exception as e:
    print(f"Error: {e}")
