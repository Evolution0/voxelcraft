from ursina import *


# 10. Create player hand
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent = camera.ui,                     # Specifies parent of hand which is the player
            model = 'assets/arm',                   # Specifies hand model
            texture = 'assets/arm_texture.png',     # Hand texture
            scale = 0.2,                            # Decrease size so it looks normal
            rotation = Vec3(160,-5,0),              # Rotate the hand to a specific angle so it doesnt face in the center of the screen
            position = Vec2(0.5,-0.6)               # Position the hand so it's connected to the "body"
        )

    # 11. Hand "animations"
    def active(self):
        self.rotation = Vec3(160,-5,0)
        self.position = Vec2(0.4,-0.5)
    
    def passive(self):
        self.position = Vec2(0.5,-0.6)
