import socket
import json
import struct
import time

# Infinite Flight Connect API v2 TCP Port
IF_PORT = 10112 

def connect_to_infinite_flight(ip_address):
    print(f"Attempting to connect to Infinite Flight at {ip_address}:{IF_PORT}...")
    
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((ip_address, IF_PORT))
        print("✅ Successfully connected to Infinite Flight!")
        return sock
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure 'Enable Infinite Flight Connect' is ON in your IF settings.")
        return None

def get_aircraft_state(sock, state_name):
    """Requests a specific piece of telemetry from the IF API."""
    try:
        # Format the command request as JSON
        request = json.dumps({"Command": "GetState", "Parameters": {"Name": state_name}})
        request_bytes = request.encode('utf-8')
        
        # The API requires a 4-byte length prefix before the JSON payload
        length_prefix = struct.pack("<I", len(request_bytes))
        sock.sendall(length_prefix + request_bytes)
        
        # Read the 4-byte length of the response
        response_length_bytes = sock.recv(4)
        if not response_length_bytes:
            return None
            
        response_length = struct.unpack("<I", response_length_bytes)[0]
        
        # Read the actual JSON response
        response_bytes = sock.recv(response_length)
        response_data = json.loads(response_bytes.decode('utf-8'))
        
        return response_data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    print("--- Infinite Flight EFB Backend ---")
    
    # You will change this to your tablet's local IP address later (e.g., 192.168.1.15)
    tablet_ip = "127.0.0.1" 
    
    connection = connect_to_infinite_flight(tablet_ip)
    
    if connection:
        print("\nListening for aircraft weight... (Press Ctrl+C to stop)")
        try:
            while True:
                # Ask IF for the aircraft's current gross weight
                weight_data = get_aircraft_state(connection, "aircraft/0/weight/gross")
                
                if weight_data:
                    weight_kg = weight_data.get("Value", 0)
                    print(f"Live Aircraft Weight: {weight_kg:,.0f} kg")
                
                # Wait 2 seconds before asking again
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\nShutting down EFB backend.")
            connection.close()
