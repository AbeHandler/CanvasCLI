'''
Handles getting the canvas API
See conda environment infomation in config/canvascli.yml

To setup, you also need to run
export CANVAS_TOKEN=10772~MBjN2XXcpUDrAkPWwrrdNDvpNYgoTMh4vldLJVD3JJoieqzYMei9kq83hNB10rHm
'''

import os

from canvasapi import Canvas

def get_api():

    # Canvas API URL
    api_url = "https://canvas.colorado.edu"
    # Canvas API key
    try:
        api_key = os.environ["CANVAS_TOKEN"]
    except KeyError:
        raise ValueError("Expecting an enviroment variable called 'CANVAS_TOKEN'. See the README for more.")

    # Initialize a new Canvas object
    return Canvas(api_url, api_key)


if __name__ == "__main__":
    canvas = get_api()