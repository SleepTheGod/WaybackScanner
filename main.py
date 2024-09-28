import argparse
import requests
import xml.etree.ElementTree as ET

def print_ascii_art():
    ascii_art = """
██     ██  █████  ██    ██     ██████   █████   ██████ ██   ██ 
██     ██ ██   ██  ██  ██      ██   ██ ██   ██ ██      ██  ██  
██  █  ██ ███████   ████       ██████  ███████ ██      █████   
██ ███ ██ ██   ██    ██        ██   ██ ██   ██ ██      ██  ██  
 ███ ███  ██   ██    ██        ██████  ██   ██  ██████ ██   ██ 
                                                               
                                                               
███████  ██████  █████  ███    ██ ███    ██ ███████ ██████     
██      ██      ██   ██ ████   ██ ████   ██ ██      ██   ██    
███████ ██      ███████ ██ ██  ██ ██ ██  ██ █████   ██████     
     ██ ██      ██   ██ ██  ██ ██ ██  ██ ██ ██      ██   ██    
███████  ██████ ██   ██ ██   ████ ██   ████ ███████ ██   ██    
                                                               
                                                               
██    ██      ██     ██████      ██████                        
██    ██     ███    ██  ████    ██  ████                       
██    ██      ██    ██ ██ ██    ██ ██ ██                       
 ██  ██       ██    ████  ██    ████  ██                       
  ████        ██ ██  ██████  ██  ██████                        
                                                                
Made by Taylor Christian Newsome
"""
    print(ascii_art)

def scan_url(base_url):
    # Define the two URL patterns for scanning
    urls_to_scan = [
        f"https://web.archive.org/cdx/search/cdx?url=*.{base_url}&output=xml&fl=original&collapse=urlkey",
        f"https://web.archive.org/cdx/search/cdx?url={base_url}*&output=xml&fl=original&collapse=urlkey"
    ]
    
    all_results = []
    
    for url in urls_to_scan:
        try:
            print(f"\nScanning: {url}")
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses

            # Check if the content is XML
            if response.content.startswith(b"<?xml"):
                # Parse the XML response
                tree = ET.ElementTree(ET.fromstring(response.content))
                root = tree.getroot()
                
                # Extract and store URLs
                for element in root:
                    for original in element:
                        all_results.append(original.text)
            else:
                print("Received non-XML content. Response content:")
                print(response.text)
        
        except requests.exceptions.RequestException as e:
            print(f"Error scanning {url}: {e}")
    
    return all_results

def print_as_curl_commands(results):
    if results:
        print("\nResults in curl commands:")
        for result in results:
            # Output each URL as a curl command
            print(f"curl {result}")
    else:
        print("\nScan done.")

def main():
    # Print ASCII art at the beginning
    print_ascii_art()
    
    # Prompt the user for a URL if not provided via command-line arguments
    url = input("\nEnter the URL to scan (e.g., api.hackerone.com): ").strip()
    
    if not url:
        print("No URL provided. Exiting.")
        return

    # Scan the provided URL
    results = scan_url(url)
    
    # Print the results as curl commands
    print_as_curl_commands(results)

if __name__ == "__main__":
    main()
