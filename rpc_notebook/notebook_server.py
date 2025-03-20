from xmlrpc.server import SimpleXMLRPCServer  # For creating the XML-RPC server
import xml.etree.ElementTree as ET              # For XML parsing and manipulation
import threading                                # To handle multiple client requests concurrently
import requests                                 # To perform HTTP requests (for the Wikipedia API)
import datetime                                 # For generating timestamps
import sys                                      # To handle command-line arguments

# Define the path to the XML database file
DB_PATH = 'notes.xml'
# Create a threading lock to ensure thread-safe operations on the XML file
LOCK = threading.Lock()

def _load_tree():
    """
    Load the XML tree from DB_PATH.
    If the file does not exist, create a new XML file with a root <data> element.
    """
    try:
        return ET.parse(DB_PATH)
    except FileNotFoundError:
        # Create a new XML tree with a root <data> element instead of <notebook>
        root = ET.Element('data')
        ET.ElementTree(root).write(DB_PATH)
        return ET.parse(DB_PATH)

def add_note(topic, text, timestamp=None):
    """
    Add a note to the specified topic.
    If the topic doesn't exist, it is created.
    """
    # Generate a timestamp in the desired format (MM/DD/YY - HH:MM:SS) if not provided.
    timestamp = timestamp or datetime.datetime.utcnow().strftime("%m/%d/%y - %H:%M:%S")
    
    with LOCK:
        tree = _load_tree()
        root = tree.getroot()
        # Find the topic element by its name attribute
        topic_el = root.find(f"./topic[@name='{topic}']")
        if topic_el is None:
            # If the topic doesn't exist, create it with the attribute name.
            topic_el = ET.SubElement(root, 'topic', {'name': topic})
        
        # Use the first 30 characters of the note text as the note's "name" attribute.
        note_name = text if len(text) <= 30 else text[:30]
        # Create the <note> element with the "name" attribute.
        note_el = ET.SubElement(topic_el, 'note', {'name': note_name})
        
        # Create a <text> subelement and set its text content.
        text_el = ET.SubElement(note_el, 'text')
        text_el.text = text
        
        # Create a <timestamp> subelement and set its text content.
        timestamp_el = ET.SubElement(note_el, 'timestamp')
        timestamp_el.text = timestamp
        
        # Pretty-print the XML for easier readability (requires Python 3.9+)
        ET.indent(tree, space="  ", level=0)
        # Write the updated XML tree back to the file.
        tree.write(DB_PATH)
    
    return True

def get_notes(topic):
    """
    Retrieve all notes for the specified topic.
    Returns a list of [timestamp, text] pairs.
    """
    with LOCK:
        tree = _load_tree()
        topic_el = tree.getroot().find(f"./topic[@name='{topic}']")
        if not topic_el:
            return []
        notes = []
        # Iterate over all <note> elements in the topic.
        for note in topic_el.findall('note'):
            # Get the text content from the <text> child.
            note_text = note.find('text').text if note.find('text') is not None else ""
            # Get the timestamp from the <timestamp> child.
            note_timestamp = note.find('timestamp').text if note.find('timestamp') is not None else ""
            notes.append([note_timestamp, note_text])
        return notes

def wiki_lookup(topic):
    """
    Query the Wikipedia API (using the opensearch protocol) for the given topic.
    Returns the URL of the first found article, or an empty string if not found.
    """
    resp = requests.get('https://en.wikipedia.org/w/api.php', params={
        'action': 'opensearch',
        'search': topic,
        'limit': 1,
        'format': 'json'
    }).json()
    return resp[3][0] if resp and len(resp[3]) else ''

def list_topics():
    """
    Return a list of all topic names in the XML database.
    """
    with LOCK:
        root = _load_tree().getroot()
        return [topic.attrib['name'] for topic in root.findall('topic')]

# Use command-line argument for port; default to 8000 if none is provided.
# This allows us to run multiple instances on different ports (e.g., 8000, 8001, etc.)
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

# Create an XML-RPC server that listens on all interfaces at the specified port.
server = SimpleXMLRPCServer(('0.0.0.0', port), allow_none=True)

# Register the functions that the client can call via RPC.
for fn in (add_note, get_notes, wiki_lookup, list_topics):
    server.register_function(fn, fn.__name__)

# Print a message to indicate that the server is running, including the port number.
print(f"Server running on port {port}…")

# Start the server; this call blocks and processes incoming RPC requests indefinitely.
server.serve_forever()