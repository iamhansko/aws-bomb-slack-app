import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from listeners.handlers import bomb

def listener(app):
    app.command("/bomb")(
        ack=respond_to_bomb_within_3_seconds,  
        lazy=[bomb.handler]  
    )

def respond_to_bomb_within_3_seconds(ack, body):
    region = body['text']
    if region is None or len(region) == 0:
        ack(":warning: No Region Name - Usage : /bomb (region name here)")
    else:
        ack(":bomb: AWS Bomb Activated. Please Wait...")