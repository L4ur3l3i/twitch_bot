from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import time
import os
from obswebsocket import obsws, requests

# Load environment variables from .env file
load_dotenv()

class ObsBot():
    def __init__(self):
        # Load credentials from environment variables
        host = os.getenv("OBS_HOST")
        port = os.getenv("OBS_PORT")
        password = os.getenv("OBS_PASSWORD")
        
        self.ws = obsws(host, port, password)
               
        try:
            self.ws.connect()
            print("Connected to OBS WebSocket successfully.")
        except Exception as e:
            print(f"Error connecting to OBS WebSocket: {e}")
        
        # Initialize ThreadPoolExecutor for non-blocking scene switches
        self.executor = ThreadPoolExecutor(max_workers=1)

    def getCurrentScene(self):
        response = self.ws.call(requests.GetCurrentProgramScene())
        return response.getSceneName()
    
    def setScene(self, scene_name):
        try:
            self.ws.call(requests.SetCurrentProgramScene(sceneName=scene_name))
        except Exception as e:
            print(f"Error setting scene: {e}")

    def switch_scene_temporarily(self, scene_name, delay):
        # Retrieve the current scene
        original_scene = self.getCurrentScene()
        if not original_scene:
            print("Failed to get the current scene. Aborting scene switch.")
            return
        
        # Switch to the specified scene
        self.setScene(scene_name)
        
        # Wait for the specified delay
        print(f"Waiting for {delay} seconds before switching back.")
        time.sleep(delay)
        
        # Switch back to the original scene
        self.setScene(original_scene)

    def switch_scene_in_background(self, scene_name, delay):
        # Run switch_scene_temporarily in a separate thread
        self.executor.submit(self.switch_scene_temporarily, scene_name, delay)

    def getAllScenes(self):
        response = self.ws.call(requests.GetSceneList())
        return response.getScenes()