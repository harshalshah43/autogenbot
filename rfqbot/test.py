from tool_functions import find_ports

message = "hi"
while True or message != 'quit':
    message = input("enter city or country: ")
    print("Suggested Ports:-")
    print(find_ports(message))

