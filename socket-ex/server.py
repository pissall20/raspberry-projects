import socket			 
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		 
print("Socket successfully created")

host = "127.0.0.1"
port = 12345				

s.bind((host, port))
s.listen(5)
# Establish connection with client. 
conn, addr = s.accept()	 
print 'Got connection from', addr 
# send a thank you message to the client. 
conn.send('Thank you for connecting') 

while True:
    print(conn.recv(1024).decode("ascii"))
    # Close the connection with the client 
    # conn.close() 
    time.sleep(1)

