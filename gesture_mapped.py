class GestureMapper:
    def _init_(self):
        self.gesture_actions = {
            "cursor_movement": "move_cursor",
            "click_action": "left_click",
            "volume_control": "adjust_volume",
            "minimize_window": "minimize_window",
            "maximize_window": "maximize_window",
            "close_window": "close_window",
            "no_gesture": "no_action",
            "no_hand": "no_action"
        }

    def get_action(self, gesture):
        return self.gesture_actions.get(gesture, "no_action")