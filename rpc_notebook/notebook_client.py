import xmlrpc.client     # XML-RPC client library for making RPC calls.
import itertools         # itertools to create a round-robin iterator.

# Server List Setup & Round-Robin
# Define the ports where your server instances are running.
ports = [8000, 8001]
# Create a list of server URLs based on the ports.
server_urls = [f'http://localhost:{port}' for port in ports]
# Create an infinite round-robin iterator over the server URLs.
server_cycle = itertools.cycle(server_urls)


def perform_rpc(method, *args):
    """
    Attempt to perform the given RPC method with arguments on each server
    in the list until one of them successfully responds.
    
    Parameters:
        method (str): The name of the RPC method to call.
        *args: Arguments to pass to the RPC method.
    
    Returns:
        The result of the RPC call, or None if all servers fail.
    """
    # Try the RPC call for as many servers as there are in the list.
    for _ in range(len(server_urls)):
        # Get the next server URL from the round-robin iterator.
        url = next(server_cycle)
        # Create an XML-RPC proxy object for this server.
        proxy = xmlrpc.client.ServerProxy(url)
        try:
            # Dynamically retrieve and call the specified RPC method with the provided arguments.
            result = getattr(proxy, method)(*args)
            return result  # Return the result if the call is successful.
        except Exception as e:
            # If an error occurs (server is down), print an error message and try the next server.
            print(f"Error contacting server {url}: {e}")
    # If no server responds successfully, print an error message.
    print("All servers failed.")
    return None

def menu():
    print("\n1) Add note")
    print("2) Fetch notes")
    print("3) Wikipedia lookup")
    print("Enter: Exit")
    return input("Choice: ")

while True:
    choice = menu()  # Display the menu and get the user's choice.
    
    if choice == '1':
        # Option 1: Add a note to the notebook.
        topic = input("Topic: ")
        text = input("Text: ")
        # Call the 'add_note' RPC method on a server.
        result = perform_rpc("add_note", topic, text)
        print("Success?", result)
    
    elif choice == '2':
        # Option 2: Fetch notes for a given topic.
        topic = input("Topic: ")
        # Call the 'get_notes' RPC method on a server.
        notes = perform_rpc("get_notes", topic)
        if not notes:
            # If no notes are found, inform the user.
            print(f"No notes found for '{topic}'.")
            # Additionally, list all available topics.
            topics = perform_rpc("list_topics")
            if topics:
                print("Available topics:", ", ".join(topics))
            else:
                print("There are currently no topics.")
        else:
            # If notes are found, display each note with its timestamp.
            for ts, txt in notes:
                print(f"{ts} — {txt}")
    
    elif choice == '3':
        # Option 3: Wikipedia lookup for a topic.
        topic = input("Wiki topic: ")
        # Call the 'wiki_lookup' RPC method on a server.
        link = perform_rpc("wiki_lookup", topic)
        if link:
            # If a link is found, display it.
            print("Found:", link)
            # Ask the user if they want to append the Wikipedia link to a notebook topic.
            if input("Append to a notebook topic? (y/n) ").lower() == 'y':
                notebook = input("Notebook topic: ")
                # Append the Wikipedia link to the specified topic using the 'add_note' RPC method.
                perform_rpc("add_note", notebook, f"Wikipedia link: {link}")
                print("Success")
        else:
            # Inform the user if no article was found.
            print("No article found.")
    
    else:
        # Any other input will exit the loop
        break