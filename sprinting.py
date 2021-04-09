from ursina import *


# 5. 1st person view
from ursina.prefabs.first_person_controller import FirstPersonController
player = FirstPersonController() # Maps the player to the 1st person view


player_speed = player.x = 1


# 14. Sprinting
class Sprint(Entity):
    global player_speed
    if held_keys['ctrl', 'w'] or held_keys['w', 'ctrl']:
        player_speed = player_speed * 2