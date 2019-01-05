import libtcodpy as libtcod

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#map
MAP_WIDTH = 80
MAP_HEIGHT = 45
color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

#lighting
color_light_ground = libtcod.Color(255, 0, 239)
color_light_wall = libtcod.Color(57, 137, 50)

#room control
ROOM_MAX_SIZE = 10
MAX_ROOM_MONSTERS = 30
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

FOV_ALGO = 0 #default FOV aglgorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

#LIMIT_FPS = 20  #20 frames-per-second maximum
class Tile:
    #a tile map and props
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False

        #default tile blocked / blocks sight
        if block_sight is None:
            block_sight = blocked
            self.block_sight = block_sight

class Rect:
    #makes rectangle lol
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) /2
        center_y = (self.y1 + self.y2) /2
        return (center_x, center_y)

    def intersect(self, other):
        #returns True if this rectangle intersects with another None
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)

class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks = False):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.blocks = blocks
        self.color = color

    def move(self, dx, dy):
        #move by the given amount
            if not is_blocked(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy


    def draw(self):
        #set the color and then draw the character that represents this object at its position
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

def is_blocked(x, y):
     #test map tiles
    if map[x][y].blocked:
        return True
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
    return False


def create_room(room):
    global map
    #go through passable tiles
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):

            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map
    #horizontal tunnel
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def make_map():
    global map, player

    #fill map with unblocked tiles
    map = [[  Tile(True)
        for y in range(MAP_HEIGHT)  ]
            for x in range(MAP_WIDTH)  ]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        #'RECT' clss makes rectangles for room
        new_room = Rect(x, y, w, h)

        #check intersect
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        #paint map tile
        if not failed:
            create_room(new_room)

            #center coords of new room
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                player.x = new_x
                player.y = new_y

            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel

                 #center coordinates of previous room
                 (prev_x, prev_y) = rooms[num_rooms - 1].center()

                 #draw a coin (random number that is either 0 or 1)
                 if libtcod.random_get_int(0, 0, 1) == 1:
                      #first move horizontally, then vertically
                      create_h_tunnel(prev_x, new_x, prev_y)
                      create_v_tunnel(prev_y, new_y, prev_x)

                 else:
                      create_v_tunnel(prev_y, new_y, prev_x)
                      create_h_tunnel(prev_x, new_x, prev_y)

            place_objects(new_room)
            rooms.append(new_room)
            num_rooms += 1

def place_objects(room):
    #choos rand num objects
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    for i in range(num_monsters):
        #choose rand spot for objects
        x = libtcod.random_get_int(0, room.x1, room.x2)
        y = libtcod.random_get_int(0, room.y1, room.y2)

        if not is_blocked(x, y):
            if libtcod.random_get_int(0, 0, 100) > 80: #80 % for norm num_monsters
                #create norm monster
                monster = Object(x, y, 'U', 'manster', libtcod.desaturated_green, blocks = True)
            else:
                #create greater monster
                monster = Object(x, y, 'P', 'MANSTER', libtcod.darker_green, blocks = True)

            objects.append(monster)

def render_all():
    global color_light_wall
    global color_light_ground
    global color_dark_ground
    global color_dark_wall
    global fov_map
    global fov_recompute
    #draw all object in list

    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    if map[x][y].explored:
                        #it's out of the player's FOV
                        if wall:
                            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET )
                        else:
                            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET )
                    else:
                        libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET)

                    map[x][y].explored = True

    for object in objects:
        object.draw()

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


def player_move_or_attack(dx, dy):
    global fov_recompute


    x = player.x + dx
    y = player.y + dy

    target = None
    for object in objects:
        if object.x == x and object.y == y:
            target = object
            break

    if target is not None:
        print "the " + target.name + "laughs at you determination"
    else:
        player.move(dx, dy)
        fov_recompute = True


def handle_keys():
    global fov_recompute
    #key = libtcod.console_check_for_keypress()  #real-time
    key = libtcod.console_wait_for_keypress(True)  #turn-based

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return "Exit"  #exit game

    if game_state == "playing":
        #movement keys
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            player_move_or_attack(0, -1)

        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            player_move_or_attack(0, 1)

        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            player_move_or_attack(-1, 0)

        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            player_move_or_attack(1, 0)

        else:
            return "didnt-take-turn"


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
#libtcod.sys_set_fps(LIMIT_FPS) real time
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

#create object representing the player
player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', "Chara", libtcod.white, blocks = True)


#the list of objects with those two
objects = [player]

make_map()

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map [x][y].block_sight, not map[x][y].blocked)

fov_recompute = True
game_state = "playing"
player_action = None
while not libtcod.console_is_window_closed():
    render_all()



    libtcod.console_flush()

    #erase all objects at their old locations, before they move
    for object in objects:
        object.clear()

    #handle keys and exit game if needed
    player_action = handle_keys()
    if player_action == "Exit":
        break

    if game_state == "playing" and player_action != "didnt-take-turn":
        for objects in object:
            if object != player:
                print "the " + object.name + " growls"
