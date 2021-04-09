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

Lower inventory - 3x9 Slot space
3rd person view
Crafting system
Upper inventory - Armor slots, character view, 4x4 crafting system
Hotbar
Sprinting
Sneaking (Crouching)
Flying
Improved jumping
Redraw Textures
Health Bar
Hunger Bar
Improved hand animations
Optimized performance
Expanded block collection - Have about 16 in total
Terrain generation
Improved void
Maximum reach - 4 blocks
Add items - Have about 16 in total
Chat
Gamemode creative - no health/hunger bar and unlimited resources
Switch between gamemodes
'''


from ursina import *


# Import separate files
from sprinting import *
from lower_inventory import *
from sky import *
from hand import *


# 1. Create basic instance of the game
app = Ursina()


# 7. Assets
grass_texture = load_texture('assets/grass_block.png')
stone_texture = load_texture('assets/stone_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')
punch_sound = Audio('assets/punch_sound', loop = False, autoplay = False)
grass_block = load_texture('assets/grass_block_3d.png') # Not created yet, will be used for lower inventory
stone_block = load_texture('assets/stone_block_3d.png') # Not created yet, will be used for lower inventory
brick_block = load_texture('assets/brick_block_3d.png') # Not created yet, will be used for lower inventory
dirt_block = load_texture('assets/dirt_block_3d.png')   # Not created yet, will be used for lower inventory


# 13. Window settings
window.fps_counter.enabled = False
window.exit_button.visible = False
window.title = 'Voxelcraft'


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


def add_item():
    global grass_block, stone_block, brick_block, dirt_block
    inventory.append(grass_block, stone_block, brick_block, dirt_block)


# 2. Create voxels
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


# 4. Create default platform
for z in range(32):                     # Creates 32 blocks on the z axis
    for x in range(32):                 # Multiplies by 32 blocks on the x axis
        voxel = Voxel(position=(x,0,z)) # Changes position of each block and creates 1024 blocks in total (32*32)


sky = Sky()   # Maps the sky
hand = Hand() # Maps the hand


# 3. Run program
app.run()
