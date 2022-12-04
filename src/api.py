import os

from canvasapi import Canvas

# setup 
# pip install canvasapi
# export CANVAS_TOKEN=10772~MBjN2XXcpUDrAkPWwrrdNDvpNYgoTMh4vldLJVD3JJoieqzYMei9kq83hNB10rHm

def get_api():

    # Canvas API URL
    api_url = "https://canvas.colorado.edu"
    # Canvas API key
    api_key = os.environ["CANVAS_TOKEN"]

    # Initialize a new Canvas object
    return Canvas(api_url, api_key)


if __name__ == "__main__":
    canvas = get_api()