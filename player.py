from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


class Player(FirstPersonController):
	def __init__(self):
		super(Player, self).__init__()
		self.camera = camera
		self.speed = 6
		camera.fov = 85
		self.mouse = mouse
		self.in_menu = False
		self.crouching = False
		self.sprinting = False