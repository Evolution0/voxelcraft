'''
Minecraft clone using Ursina Game-Engine for Python (3.9).
Project status: Open-source
Original version: https://github.com/pokepetter/ursina/blob/master/samples/minecraft_clone.py
Contributor/s:
'''


'''
GOAL:

Add as many features to match the original game as possible until January 1st, 2022


PROBLEMS:

1. If too many blocks are added, the game slows down very noticeably.
2. There are a lot of gaps between textures which is caused by poorly drawn textures,
can be improved by redrawing them.


TO-DO:

1. Lower inventory (items) - DOING
2. Hotbar
3. Crouch
4. Improve jumping
5. Redraw textures
6. Improve void
7. Fly
8. Improve hand animations
9. Sprint
10. Maximum block removing reach: 4 blocks
11. Keep breaking/adding blocks after first one
12. Terrain generation
13. Crafting system
14. Upper inventory (armor, crafting, etc)
'''


from ursina import *


# 1. Create basic instance of the game
app = Ursina()


# 7. Assets
grass_texture = load_texture('assets/grass_block.png')
stone_texture = load_texture('assets/stone_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')
sky_texture = load_texture('assets/skybox.png')
arm_texture = load_texture('assets/arm_texture.png')
punch_sound = Audio('assets/punch_sound', loop = False, autoplay = False)
grass_block = load_texture('assets/grass_block_3d.png') # Not created yet, will be used for lower inventory
stone_block = load_texture('assets/stone_block_3d.png') # Not created yet, will be used for lower inventory
brick_block = load_texture('assets/brick_block_3d.png') # Not created yet, will be used for lower inventory
dirt_block = load_texture('assets/dirt_block_3d.png')   # Not created yet, will be used for lower inventory


# 13. Window settings
window.fps_counter.enabled = False
window.exit_button.visible = False


# 8. Picking blocks
block_pick = 1 # Default block is grass block

def update():
    global block_pick
    # If block is destroyed, active hand animation is played
    if held_keys['left mouse']:
        hand.active()
    else:
        hand.passive()
    # If keys "1", "2", "3" or "4" are pressed, change between grass, stone, brick and dirt blocks
    if held_keys['1']: block_pick = 1 # Grass block
    if held_keys['2']: block_pick = 2 # Stone block
    if held_keys['3']: block_pick = 3 # Brick block
    if held_keys['4']: block_pick = 4 # Dirt block


# 5. 1st person view
from ursina.prefabs.first_person_controller import FirstPersonController
camera.fov = 85
player = FirstPersonController() # Maps the player to the 1st person view


player_speed = player.x = 1


# 14. Sprinting
class Sprint(Entity):
    global player_speed
    if held_keys['ctrl', 'w'] or held_keys['w', 'ctrl']:
        player_speed = player_speed * 2


# 15. Inventory
class Lower_Inventory(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent = camera.ui,
            model = Quad(radius=0),
            texture = 'white_cube',
            texture_scale = (9,3),
            scale = (.9, .3),
            origin = (-.5, .8),
            position = (-0.45,0.15),
            color = color.rgb(210, 210, 210)
            )

        for key, value in kwargs.items():
            setattr(self, key, value)


    def find_free_spot(self):
        for y in range(8):
            for x in range(5):
                grid_positions = [(int(e.x*self.texture_scale[0]), int(e.y*self.texture_scale[1])) for e in self.children]
                print(grid_positions)

                if not (x,-y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y


    def append(self, item, x=0, y=0):
        if len(self.children) >= 5*8:
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent = self,
            model = 'quad',
            texture = item,
            color = color.white,
            scale_x = 1/self.texture_scale[0],
            scale_y = 1/self.texture_scale[1],
            origin = (-.5,.5),
            x = x * 1/self.texture_scale[0],
            y = -y * 1/self.texture_scale[1],
            z = -.5,
            )


        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01   # Ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x/2)) * 5) / 5
            icon.y = int((icon.y - (icon.scale_y/2)) * 8) / 8
            icon.z += .01

            # If outside, return to original position
            if icon.x < 0 or icon.x >= 1 or icon.y > 0 or icon.y <= -1:
                icon.position = (icon.org_pos)
                return

            # If the spot is taken, swap positions
            for c in self.children:
                if c == icon:
                    continue
                if c.x == icon.x and c.y == icon.y:
                    print('swap positions')
                    c.position = icon.org_pos

        icon.drag = drag
        icon.drop = drop


# lower_inventory = Lower_Inventory()     # <----- UN-COMMENT LINE FOR THE INVENTORY TO BE VISIBLE IN THE GAME


def add_item():
    global grass_block, stone_block, brick_block, dirt_block
    inventory.append(grass_block, stone_block, brick_block, dirt_block)


# 2. Create voxel (minecraft block) as a button
class Voxel(Button):
    def __init__(self, position = (0,0,0), texture = grass_texture):
        # Ends up with default position if no information is being passed
        # and the grass texture is being selected as default
        super().__init__(
            parent = scene,                                 # Specifies parent of voxel so it scales properly
            position = position,                            # Right in the middle
            model = 'assets/block',                         # Specifies voxel model
            origin_y = 0.5,                                 # Specifies y origin
            texture = texture,                              # Voxel texture
            color = color.color(0,0,random.uniform(0.9,1)), # Every shade of the block is random
            scale = 0.5                                     # Solve zoomed-in perspective by scaling out the game
        )

    # 6. Create and destroy blocks
    def input(self,key):
        if self.hovered:
            global lower_inventory
            if key == 'right mouse down': # If right mouse button is pressed, create new block
                punch_sound.play()
                # Be able to place different blocks depending on the number pressed
                if block_pick == 1: voxel = Voxel(position=self.position + mouse.normal, texture=grass_texture) # Place grass block
                if block_pick == 2: voxel = Voxel(position=self.position + mouse.normal, texture=stone_texture) # Place stone block
                if block_pick == 3: voxel = Voxel(position=self.position + mouse.normal, texture=brick_texture) # Place brick block
                if block_pick == 4: voxel = Voxel(position=self.position + mouse.normal, texture=dirt_texture) # Place dirt block
            if key == 'left mouse down': # If left mouse button is pressed, destroy block
                punch_sound.play()
                while destroy(self) == True:
                    destroy(voxel)
            if key == 'space down': # If space is pressed, jump one block
                player.y += 1
                invoke(setattr, player, 'y', player.y-1)
            # Open inventory
            if held_keys['e down']:
                    lower_inventory.visible = True
                    mouse.visible = True


# 9. Create sky
class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent = scene,          # Specifies parent of sky so it scales properly
            model = 'sphere',        # Specifies sky model
            texture = sky_texture,   # Sky texture
            scale = 1000,            # Increases size drastically
            double_sided = True      # See the sphere when you are in it
        )


# 10. Create player hand
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent = camera.ui,        # Specifies parent of hand which is the player
            model = 'assets/arm',      # Specifies hand model
            texture = arm_texture,     # Hand texture
            scale = 0.2,               # Decrease size so it looks normal
            rotation = Vec3(160,-5,0), # Rotate the hand to a specific angle so it doesnt face in the center of the screen
            position = Vec2(0.5,-0.6)  # Position the hand so it's connected to the "body"
        )

    # 11. Hand "animations"
    def active(self):
        self.rotation = Vec3(160,-5,0)
        self.position = Vec2(0.4,-0.5)
    
    def passive(self):
        self.position = Vec2(0.5,-0.6)


# 4. Create default platform
for z in range(32):                     # Creates 32 blocks on the z axis
    for x in range(32):                 # Multiplies by 32 blocks on the x axis
        voxel = Voxel(position=(x,0,z)) # Changes position of each block and creates 1024 blocks in total (32*32)


sky = Sky()   # Maps the sky
hand = Hand() # Maps the hand


# 3. Run program
app.run()
