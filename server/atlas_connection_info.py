import socket
import sys
import ssl
import urllib.request
import json

def check_mongodb_hostname(hostname="cluster0.rpkmj.mongodb.net", port=27017):
    print(f"Testing connection to MongoDB Atlas hostname: {hostname}:{port}")
    try:
        # Try to create a socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # Get IP address
        ip_address = socket.gethostbyname(hostname)
        print(f"Resolved {hostname} to IP: {ip_address}")
        
        # Try connecting
        result = sock.connect_ex((hostname, port))
        
        if result == 0:
            print(f"Successfully connected to {hostname}:{port}")
        else:
            print(f"Could not connect to {hostname}:{port}, error code: {result}")
            print(f"Error meaning: {socket.errorTab.get(result, 'Unknown error')}")
        
        sock.close()
    except socket.gaierror:
        print(f"Hostname {hostname} could not be resolved")
    except socket.error as e:
        print(f"Socket error: {e}")

def get_public_ip():
    print("Checking public IP address...")
    try:
        # Use a service to get our public IP
        response = urllib.request.urlopen('https://api.ipify.org?format=json')
        data = json.loads(response.read().decode('utf-8'))
        ip = data['ip']
        print(f"Your public IP address is: {ip}")
        print("⚠️ Make sure this IP is whitelisted in MongoDB Atlas Network Access settings")
    except Exception as e:
        print(f"Could not determine public IP: {e}")

if __name__ == "__main__":
    print("==== MongoDB Atlas Connection Diagnostic ====")
    
    # Check Python version
    python_version = sys.version
    print(f"Python version: {python_version}")
    
    # Check pymongo version
    try:
        import pymongo
        print(f"PyMongo version: {pymongo.__version__}")
    except ImportError:
        print("PyMongo is not installed")
    
    # Check SSL/TLS support
    print(f"SSL version: {ssl.OPENSSL_VERSION}")
    
    # Check hostname resolution
    check_mongodb_hostname()
    
    # Get public IP
    get_public_ip()
    
    print("\n==== Diagnostic Complete ====")
    print("If you're seeing authentication errors despite using the correct credentials,")
    print("please check that your IP address is whitelisted in MongoDB Atlas Network Access settings")
    print("You may need to add a new entry in MongoDB Atlas -> Network Access -> ADD IP ADDRESS")
    print("Either add your specific IP or allow access from anywhere with 0.0.0.0/0") 