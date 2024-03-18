import os
import ssl

import sys
import socket
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup




def fetchWebPage(hostname, endpoint, redirectCount=0, maxRedirects=5):
    """Fetches a web page using HTTPS."""
    try:
        sslContext = ssl.create_default_context()
        with sslContext.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname) as socketWrapped:
            socketWrapped.connect((hostname, 443))
            requestHeader = f"GET {endpoint} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
            socketWrapped.sendall(requestHeader.encode())
            responseBytes = b''
            while chunk := socketWrapped.recv(1024):
                responseBytes += chunk
        responseText = responseBytes.decode("utf-8", errors="ignore")
        headers = responseText.split("\r\n")

        if headers[0].startswith("HTTP/1.1 3"):
            locationHeader = next((line.split(": ", 1)[1].strip() for line in headers if line.startswith("Location:")), None)
            if locationHeader:
                parsedLocation = urlparse(locationHeader)
                if redirectCount < maxRedirects:
                    return fetchWebPage(parsedLocation.netloc, parsedLocation.path, redirectCount + 1, maxRedirects)
        pageContent = BeautifulSoup(responseBytes, 'html.parser')
        return pageContent, pageContent.get_text(strip=True)
    except Exception as error:
        return f"Error: {str(error)}"

def displayWebContent(contentSoup):
    """Displays selected elements from the web content."""
    for element in contentSoup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'ul', 'li']):
        tagType = element.name
        if tagType in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            headerText = '\n' + element.text
            print(headerText)
            print('-' * len(headerText))
        elif tagType == 'p':
            print('\n' + element.text)
        elif tagType == 'a':
            print(f"\nLink: {element.get('href')}")
        elif tagType in ['ul', 'li']:
            print(f"{'  - ' if tagType == 'li' else ''}{element.text}")



def showInstructions():
    """Prints usage instructions."""
    print("Commands:")
    print("  go2web -u <URL>            Fetch and display content from <URL>")
    print("  go2web -s <search-query>    Search <search-query> on Google and display results")
    print("  go2web -h                  Show this help message")

def main():
    if len(sys.argv) < 3:
        showInstructions()
        return
    option, argument = sys.argv[1], ' '.join(sys.argv[2:])
    if option == '-u':
        parsedUrl = urlparse(argument)
        webContent = fetchWebPage(parsedUrl.netloc, parsedUrl.path or '/')
        if isinstance(webContent, tuple):
            contentSoup, _ = webContent
            displayWebContent(contentSoup)
        else:
            print(webContent)

    elif option == '-h':
        showInstructions()
    else:
        print("Unknown option. Use '-h' for help.")

if __name__ == "__main__":
    main()
