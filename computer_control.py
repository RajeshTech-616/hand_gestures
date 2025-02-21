import pyautogui
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class ComputerControl:
    def _init_(self):
        pyautogui.FAILSAFE = True
        self.last_action_time = time.time()
        
        # Initialize volume control
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume.iid, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Cooldown times for different actions
        self.action_cooldowns = {
            "move_cursor": 0.01,
            "left_click": 0.3,
            "right_click": 0.3,
            "adjust_volume": 0.1,
            "minimize_window": 0.5,
            "maximize_window": 0.5,
            "close_window": 0.5
        }
        
        # Screen dimensions for cursor mapping
        self.screen_width, self.screen_height = pyautogui.size()
        pyautogui.PAUSE = 0.1

    def execute_command(self, command, cursor_pos=None, additional_data=None):
        current_time = time.time()
        cooldown = self.action_cooldowns.get(command, 0.5)
        
        if current_time - self.last_action_time < cooldown:
            return

        try:
            if command == "move_cursor" and cursor_pos is not None:
                # Map hand coordinates to screen coordinates
                screen_x = int(cursor_pos[0] * self.screen_width)
                screen_y = int(cursor_pos[1] * self.screen_height)
                # Add smoothing
                pyautogui.moveTo(screen_x, screen_y, duration=0.1)
            
            elif command == "left_click":
                pyautogui.click()
            
            elif command == "right_click":
                pyautogui.rightClick()
            
            elif command == "adjust_volume":
                if additional_data:
                    # Map pinch distance to volume range (-65.25 to 0.0)
                    volume_level = (1 - additional_data) * -65.25
                    self.volume.SetMasterVolumeLevel(volume_level, None)
            
            elif command == "minimize_window":
                pyautogui.hotkey('win', 'down')
            
            elif command == "maximize_window":
                pyautogui.hotkey('win', 'up')
            
            elif command == "close_window":
                pyautogui.hotkey('alt', 'f4')

            self.last_action_time = current_time

        except Exception as e:
            print(f"Error executing command {command}: {e}")

    def map_coordinates(self, hand_x, hand_y):
        """Map hand coordinates (0-1) to screen coordinates"""
        screen_x = int(hand_x * self.screen_width)
        screen_y = int(hand_y * self.screen_height)
        return screen_x, screen_y

    def smooth_movement(self, target_x, target_y, duration=0.1):
        """Implement smooth cursor movement"""
        current_x, current_y = pyautogui.position()
        pyautogui.moveTo(target_x, target_y, duration=duration)