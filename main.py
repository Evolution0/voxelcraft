"""
Minecraft clone using Ursina Game-Engine for Python (3.9).
Project status: Open-source
Original version: https://github.com/pokepetter/ursina/blob/master/samples/minecraft_clone.py
Contributor/s:
"""
import ursina.application

"""
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
"""

from ursina import *

# Import separate files
from sprinting import *
from player import *
# from inventory import *
import sky
from hand import *

# 1. Create basic instance of the game
app = Ursina()

# 7. Assets
grass_texture = load_texture('assets/grass_block.png')
stone_texture = load_texture('assets/stone_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')

inventory_slot_texture = load_texture('assets/inventory_slot.png')
boots_slot_texture = load_texture('assets/boots_slot.png')
leggings_slot_texture = load_texture('assets/leggings_slot.png')
chestplate_slot_texture = load_texture('assets/chestplate_slot.png')
helmet_slot_texture = load_texture('assets/helmet_slot.png')
shield_slot_texture = load_texture('assets/shield_slot.png')

punch_sound = Audio('assets/punch_sound', loop=False, autoplay=False)

grass_block = load_texture('assets/grass_block_3d.png')  # Not created yet, will be used for lower inventory
stone_block = load_texture('assets/stone_block_3d.png')  # Not created yet, will be used for lower inventory
brick_block = load_texture('assets/brick_block_3d.png')  # Not created yet, will be used for lower inventory
dirt_block = load_texture('assets/dirt_block_3d.png')  # Not created yet, will be used for lower inventory

# 13. Window settings
window.fps_counter.color = color.red
window.fps_counter.enabled = True
window.exit_button.visible = False
window.title = 'Voxelcraft'

# 8. Picking blocks
block_pick = 1  # Default block is grass block


def update():
    global block_pick
    global menu
    # If block is destroyed, active hand animation is played
    if held_keys['left mouse']:
        hand.active()
    else:
        hand.passive()

    # If keys "1", "2", "3" or "4" are pressed, change between grass, stone, brick and dirt blocks
    if held_keys['1']:
        block_pick = 1  # Grass block
    if held_keys['2']:
        block_pick = 2  # Stone block
    if held_keys['3']:
        block_pick = 3  # Brick block
    if held_keys['4']:
        block_pick = 4  # Dirt block

    if held_keys['control'] and player.crouching is False:
        # FOV increase should be based on time delta, its too sudden currently.
        player.sprinting = True
        player.speed = 12
        player.camera.fov = 100
    else:
        player.sprinting = False
        player.speed = 6
        player.camera.fov = 85

    if held_keys['alt']:
        # Crouching needs to be smoother, add time delta to camera position change.
        player.crouching = True
        player.camera.position = (0, -1, 0)
    else:
        player.crouching = False
        player.camera.position = (0, 0, 0)

    if held_keys['escape'] and player.in_menu is False:
        # Keys flit by too fast, need some way to prevent "bounce"
        player.mouse.locked = False
        # Switch this out for a proper menu rather than a single button.
        menu = Button(text='QUIT', color=color.black, scale=.10, text_origin=(0, 0))
        menu.on_click = application.quit
        player.in_menu = True

    if player.in_menu is True:
        # If in a menu close it and go back to previous; if at "bottom level" then resume the game.
        # Need some way to track "where" we are (Current menu, previous menu)
        print("In a menu!")
        if held_keys['escape']:
            destroy(menu)
            player.mouse.locked = True
            player.in_menu = False


# 15. Lower Inventory
class LowerInventory(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=0),
            texture=inventory_slot_texture,
            texture_scale=(9, 3),
            scale=(0.72, 0.24),
            origin=(-0.32, 0.62),
            position=(-0.23, -0.03),
            color=color.rgb(255, 255, 255)
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

    def find_free_spot(self):
        for y in range(3):
            for x in range(9):
                grid_positions = [(int(e.x * self.texture_scale[0]), int(e.y * self.texture_scale[1])) for e in
                                  self.children]
                print(grid_positions)

                if not (x, -y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y

    def append(self, item, x=0, y=0):
        if len(self.children) >= 9 * 3:
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent=self,
            model='quad',
            texture=item,
            color=color.white,
            scale_x=1 / self.texture_scale[0],
            scale_y=1 / self.texture_scale[1],
            origin=(-.5, .5),
            x=x * 1 / self.texture_scale[0],
            y=-y * 1 / self.texture_scale[1],
            z=-.5,
        )

        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01  # Ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x / 2)) * 9) / 9
            icon.y = int((icon.y - (icon.scale_y / 2)) * 3) / 3
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
                    c.position = icon.org_pos

        icon.drag = drag
        icon.drop = drop


# 16. Hotbar
class Hotbar(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=0),
            texture=inventory_slot_texture,
            texture_scale=(9, 1),
            scale=(0.72, 0.08),
            origin=(-0.32, 0.62),
            position=(-0.23, -0.315),
            color=color.rgb(255, 255, 255)
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

    def find_free_spot(self):
        for y in range(1):
            for x in range(9):
                grid_positions = [(int(e.x * self.texture_scale[0]), int(e.y * self.texture_scale[1])) for e in
                                  self.children]
                print(grid_positions)

                if not (x, -y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y

    def append(self, item, x=0, y=0):
        if len(self.children) >= 9 * 1:
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent=self,
            model='quad',
            texture=item,
            color=color.white,
            scale_x=1 / self.texture_scale[0],
            scale_y=1 / self.texture_scale[1],
            origin=(-.5, .5),
            x=x * 1 / self.texture_scale[0],
            y=-y * 1 / self.texture_scale[1],
            z=-.5,
        )

        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01  # Ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x / 2)) * 9) / 9
            icon.y = int((icon.y - (icon.scale_y / 2)) * 1) / 1
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
                    c.position = icon.org_pos

        icon.drag = drag
        icon.drop = drop


# 17. a. Armor slot: Boots
class Boots_Slot(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=0),
            texture=boots_slot_texture,
            texture_scale=(1, 1),
            scale=(0.08, 0.08),
            origin=(1.12, -2.27),
            position=(-0.23, -0.18),
            color=color.rgb(255, 255, 255)
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

    def find_free_spot(self):
        for y in range(1):
            for x in range(1):
                grid_positions = [(int(e.x * self.texture_scale[0]), int(e.y * self.texture_scale[1])) for e in
                                  self.children]
                print(grid_positions)

                if not (x, -y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y

    def append(self, item, x=0, y=0):
        if len(self.children) >= 1 * 1:
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent=self,
            model='quad',
            texture=item,
            color=color.white,
            scale_x=1 / self.texture_scale[0],
            scale_y=1 / self.texture_scale[1],
            origin=(-.5, .5),
            x=x * 1 / self.texture_scale[0],
            y=-y * 1 / self.texture_scale[1],
            z=-.5,
        )

        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01  # Ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x / 2)) * 1) / 1
            icon.y = int((icon.y - (icon.scale_y / 2)) * 1) / 1
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
                    c.position = icon.org_pos

        icon.drag = drag
        icon.drop = drops

        # def add_item(): # Can only add boots
        # global iron_boots
        # inventory.append(iron_boots)


# 17. b. Armor slot: Leggings
class Leggings_Slot(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=0),
            texture=leggings_slot_texture,
            texture_scale=(1, 1),
            scale=(0.08, 0.08),
            origin=(1.12, -2.27),
            position=(-0.23, -0.1),
            color=color.rgb(255, 255, 255)
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

    def find_free_spot(self):
        for y in range(1):
            for x in range(1):
                grid_positions = [(int(e.x * self.texture_scale[0]), int(e.y * self.texture_scale[1])) for e in
                                  self.children]
                print(grid_positions)

                if not (x, -y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y

    def append(self, item, x=0, y=0):
        if len(self.children) >= 1 * 1:
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent=self,
            model='quad',
            texture=item,
            color=color.white,
            scale_x=1 / self.texture_scale[0],
            scale_y=1 / self.texture_scale[1],
            origin=(-.5, .5),
            x=x * 1 / self.texture_scale[0],
            y=-y * 1 / self.texture_scale[1],
            z=-.5,
        )

        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01  # Ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x / 2)) * 1) / 1
            icon.y = int((icon.y - (icon.scale_y / 2)) * 1) / 1
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
                    c.position = icon.org_pos

        icon.drag = drag
        icon.drop = drops

        # def add_item(): # Can only add leggings
        # global iron_leggings
        # inventory.append(iron_leggings)


# 17. c. Armor slot: Chestplate
class Chestplate_Slot(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=0),
            texture=chestplate_slot_texture,
            texture_scale=(1, 1),
            scale=(0.08, 0.08),
            origin=(1.12, -2.27),
            position=(-0.23, -0.02),
            color=color.rgb(255, 255, 255)
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

    def find_free_spot(self):
        for y in range(1):
            for x in range(1):
                grid_positions = [(int(e.x * self.texture_scale[0]), int(e.y * self.texture_scale[1])) for e in
                                  self.children]
                print(grid_positions)

                if not (x, -y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y

    def append(self, item, x=0, y=0):
        if len(self.children) >= 1 * 1:
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent=self,
            model='quad',
            texture=item,
            color=color.white,
            scale_x=1 / self.texture_scale[0],
            scale_y=1 / self.texture_scale[1],
            origin=(-.5, .5),
            x=x * 1 / self.texture_scale[0],
            y=-y * 1 / self.texture_scale[1],
            z=-.5,
        )

        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01  # Ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x / 2)) * 1) / 1
            icon.y = int((icon.y - (icon.scale_y / 2)) * 1) / 1
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
                    c.position = icon.org_pos

        icon.drag = drag
        icon.drop = drops

        # def add_item(): # Can only add chestplates
        # global iron_chestplate
        # inventory.append(iron_chestplate)


# 17. d. Armor slot: Helmet
class Helmet_Slot(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=0),
            texture=helmet_slot_texture,
            texture_scale=(1, 1),
            scale=(0.08, 0.08),
            origin=(1.12, -2.27),
            position=(-0.23, 0.06),
            color=color.rgb(255, 255, 255)
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

    def find_free_spot(self):
        for y in range(1):
            for x in range(1):
                grid_positions = [(int(e.x * self.texture_scale[0]), int(e.y * self.texture_scale[1])) for e in
                                  self.children]
                print(grid_positions)

                if not (x, -y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y

    def append(self, item, x=0, y=0):
        if len(self.children) >= 1 * 1:
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent=self,
            model='quad',
            texture=item,
            color=color.white,
            scale_x=1 / self.texture_scale[0],
            scale_y=1 / self.texture_scale[1],
            origin=(-.5, .5),
            x=x * 1 / self.texture_scale[0],
            y=-y * 1 / self.texture_scale[1],
            z=-.5,
        )

        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01  # Ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x / 2)) * 1) / 1
            icon.y = int((icon.y - (icon.scale_y / 2)) * 1) / 1
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
                    c.position = icon.org_pos

        icon.drag = drag
        icon.drop = drops

        # def add_item(): # Can only add helmets
        # global iron_helmet
        # inventory.append(iron_helmet)


# 17. e. Shield slot
class Shield_Slot(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=0),
            texture=shield_slot_texture,
            texture_scale=(1, 1),
            scale=(0.08, 0.08),
            origin=(1.12, -2.27),
            position=(0.08, -0.18),
            color=color.rgb(255, 255, 255)
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

    def find_free_spot(self):
        for y in range(1):
            for x in range(1):
                grid_positions = [(int(e.x * self.texture_scale[0]), int(e.y * self.texture_scale[1])) for e in
                                  self.children]
                print(grid_positions)

                if not (x, -y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y

    def append(self, item, x=0, y=0):
        if len(self.children) >= 1 * 1:
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent=self,
            model='quad',
            texture=item,
            color=color.white,
            scale_x=1 / self.texture_scale[0],
            scale_y=1 / self.texture_scale[1],
            origin=(-.5, .5),
            x=x * 1 / self.texture_scale[0],
            y=-y * 1 / self.texture_scale[1],
            z=-.5,
        )

        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01  # Ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x / 2)) * 1) / 1
            icon.y = int((icon.y - (icon.scale_y / 2)) * 1) / 1
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
                    c.position = icon.org_pos

        icon.drag = drag
        icon.drop = drops

        # def add_item(): # Can only add helmets
        # global iron_helmet
        # inventory.append(iron_helmet)


# 17. f. Inventory Crafting
class Inventory_Crafting_Grid(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=0),
            texture=inventory_slot_texture,
            texture_scale=(2, 2),
            scale=(0.16, 0.16),
            origin=(1.12, -2.27),
            position=(0.3, -0.2),
            color=color.rgb(255, 255, 255)
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

    def find_free_spot(self):
        for y in range(2):
            for x in range(2):
                grid_positions = [(int(e.x * self.texture_scale[0]), int(e.y * self.texture_scale[1])) for e in
                                  self.children]
                print(grid_positions)

                if not (x, -y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y

    def append(self, item, x=0, y=0):
        if len(self.children) >= 2 * 2:
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent=self,
            model='quad',
            texture=item,
            color=color.white,
            scale_x=1 / self.texture_scale[0],
            scale_y=1 / self.texture_scale[1],
            origin=(-.5, .5),
            x=x * 1 / self.texture_scale[0],
            y=-y * 1 / self.texture_scale[1],
            z=-.5,
        )

        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z -= .01  # Ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x / 2)) * 2) / 2
            icon.y = int((icon.y - (icon.scale_y / 2)) * 2) / 2
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
                    c.position = icon.org_pos

        icon.drag = drag
        icon.drop = drops

        # def add_item(): # Can only add helmets
        # global iron_helmet
        # inventory.append(iron_helmet)


# 17. g. Inventory Crafting
class Inventory_Crafting_Output(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=0),
            texture=inventory_slot_texture,
            texture_scale=(1, 1),
            scale=(0.08, 0.08),
            origin=(1.12, -2.27),
            position=(0.42, -0.02),
            color=color.rgb(255, 255, 255)
        )

        for key, value in kwargs.items():
            setattr(self, key, value)


# UN-COMMENT LINES BELOW UNTIL KEY PRESSING IS SOLVED FOR THE INVENTORIES TO BE VISIBLE IN-GAME

# inventory = Lower_Inventory(), Hotbar(), Boots_Slot(), Leggings_Slot(), Chestplate_Slot(), Helmet_Slot(),
# Shield_Slot(), Inventory_Crafting_Grid(), Inventory_Crafting_Output()


# 2. Create voxels
class Voxel(Entity):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        # Ends up with default position if no information is being passed
        # and the grass texture is being selected as default
        super().__init__(
            parent=scene,  # Specifies parent of voxel so it scales properly
            position=position,  # Right in the middle
            model='cube',  # Specifies voxel model
            origin_y=0.5,  # Specifies y origin
            texture=texture,  # Voxel texture
            color=color.color(0, 0, random.uniform(0.9, 1)),  # Every shade of the block is random
            scale=1  # Solve zoomed-in perspective by scaling out the game
        )
        self.collider = self.model

    # 6. Create and destroy blocks
    def input(self, key):
        if self.hovered:
            if key == 'right mouse down':  # If right mouse button is pressed, create new block
                punch_sound.play()
                # Be able to place different blocks depending on the number pressed
                if block_pick == 1: voxel = Voxel(position=self.position + mouse.normal,
                                                  texture=grass_texture)  # Place grass block
                if block_pick == 2: voxel = Voxel(position=self.position + mouse.normal,
                                                  texture=stone_texture)  # Place stone block
                if block_pick == 3: voxel = Voxel(position=self.position + mouse.normal,
                                                  texture=brick_texture)  # Place brick block
                if block_pick == 4: voxel = Voxel(position=self.position + mouse.normal,
                                                  texture=dirt_texture)  # Place dirt block
            if key == 'left mouse down':  # If left mouse button is pressed, destroy block
                punch_sound.play()
                while destroy(self) is True:
                    destroy(voxel)
            if key == 'space down':  # If space is pressed, jump one block
                player.y += 1
                invoke(setattr, player, 'y', player.y - 1)


# 4. Create default platform
for z in range(32):  # Creates 32 blocks on the z axis
    for x in range(32):  # Multiplies by 32 blocks on the x axis
        voxel = Voxel(position=(x, 0, z))  # Changes position of each block and creates 1024 blocks in total (32*32)

sky = sky.Sky()  # Maps the sky
hand = Hand()  # Maps the hand

player = Player()  # Maps the player to the 1st person view

# 3. Run program
app.run()
