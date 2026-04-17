import os
import sys
from threading import Timer
from flask import Flask
from pyngrok import ngrok
from main import app

# Set your ngrok auth token if you have one (optional but recommended)
ngrok.set_auth_token("36BuKde9AfKCmFbhug8rBkpeAaU_6X3X6Hu6JsTQgR1Gnrr1x")

def open_browser():
    # Get the public URL
    public_url = ngrok.connect(5501, domain="unautographed-cornelia-nonbibulously.ngrok-free.dev").public_url
    print(f" * Public URL: {public_url}")
    print(" * Share this link with your friend!")

if __name__ == "__main__":
    # Open ngrok tunnel after a short delay
    Timer(1, open_browser).start()
    
    # Run the app
    app.run(port=5501)
