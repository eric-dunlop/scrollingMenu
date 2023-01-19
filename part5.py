# Author: Eric Dulop
# Purpose: Simple menu that reads sesors and displays their data
# on an lcd. controlled using a rotery encoder
# date: 2022-10-23
# ITSC-305 A4-5 



from gpiozero import Button
from time import sleep
import i2c_led_driver as lcd_d
from smbus import SMBus

# very similar to the Page class right below here
# with added "sens_function", a function that dertermins
# how the sesor data will be displayed
class Sensor:

    def __init__(self, sensor, sens_function, jump=None):
        self.sensor = sensor
        self.jump = jump
        self.sens_function = sens_function

    # passed to avoid errors, the sensors do not have adjacent pages
    def get_next_page(self):
        pass

    def get_prev_page(self):
        pass
        
    def jump(self):
        return self.jump

    def set_jump(self, jump):
        self.jump = jump

    # displays the .sensor attibute centered
    # calls self.sens_function to display sensor data
    def display_page(self):
        global mylcd
        mylcd.lcd_clear()
        mylcd.lcd_display_string(self.sensor,1 ,int((16 - len(self.sensor))/2))
        self.sens_function()


# object that represents a page of the menu system
# are arranged in doubly linked lists that are traversed by
# turning the rotery encoder
# the jump method is used to jump to another linked list or a sensor
class Page:

    def __init__(self, text, jump=None, next_page=None, prev_page=None):
        self.next_page = next_page
        self.text = text
        self.jump = jump
        self.prev_page = prev_page
        
    # getters and setters for connected pages
    def set_next_page(self, next_page):
        self.next_page = next_page

    def get_next_page(self):
        return self.next_page

    def set_prev_page(self, prev_page):
        self.prev_page = prev_page

    def get_prev_page(self):
        return self.prev_page

    def get_sensor(self):
        return self.sensor

    def set_jump(self, jump):
        self.jump = jump

    def jump(self):
        return self.jump

    # displays the page information on the lcd
    def display_page(self):
        global mylcd
        mylcd.lcd_clear()
        mylcd.lcd_display_string(self.text,1 ,int((16 - len(self.text))/2))

# class of the linke list objects tracks the start and end of each page list
class Menu:

    def __init__(self):
        self.first_page = None
        self.last_page = None

    def add_page(self, text):
        new_page = Page(text)
        current_end = self.last_page
        if current_end != None:
            current_end.set_next_page(new_page)
            new_page.set_prev_page(current_end)
        self.last_page = new_page
        
        if self.first_page == None:
            self.first_page = new_page


# functions that control how sensors are displayed and called 
# when the Sensor object is set as the current_page
def not_sensor():
    mylcd.lcd_display_string("not a sensor",2 ,2)

def read_photo():
    mylcd.lcd_display_string(hex(photo),2 ,5)

def read_touch():
    if touch == 0xff: mylcd.lcd_display_string("off",2 ,6)
    else: mylcd.lcd_display_string("active",2 ,5)

def read_pot():
    mylcd.lcd_display_string(f"{int(pot/255*100)}%", 2 ,6)


# some variables needed for running
channel1 = Button(20)
channel2 = Button(21)
push = Button(26)
bus = SMBus(1)
mylcd = lcd_d.lcd()


# this is where the linked lists built and connected.
# if time try to make this better maybe with a a way to traverse
# the linke list and add jumps after they ar fully built (if time)

# usless sub menu for proof of concept
tree1 = Menu()
tree1.add_page("This is")
tree1.add_page("Filler")
tree1.add_page("Go Back")

# start point menu started
start_menu = Menu()
start_menu.add_page("Start Here")
start_menu.add_page("tree 1")

# create jumops to and from the tree 1 menu
start_menu.last_page.set_jump(tree1.first_page)
tree1.last_page.set_jump(start_menu.first_page)

# sensor objects are built
photo = Sensor("Photo", read_photo)
touch = Sensor("Touch", read_touch)
pot = Sensor("Pot", read_pot)

# make the sens menu
# add jumps to the sensors and back
sens_menu = Menu()
sens_menu.add_page("Photo Sensor")
photo.set_jump(sens_menu.last_page)
sens_menu.last_page.set_jump(photo)

sens_menu.add_page("Touch Sensor")
touch.set_jump(sens_menu.last_page)
sens_menu.last_page.set_jump(touch)

sens_menu.add_page("Potentiometer")
pot.set_jump(sens_menu.last_page)
sens_menu.last_page.set_jump(pot)

sens_menu.add_page("Go Back")
start_menu.add_page("sensors")

# set jumps between sens menu and start menu
start_menu.last_page.set_jump(sens_menu.first_page)
sens_menu.last_page.set_jump(start_menu.first_page)


# puts us at the start menu
current_page = start_menu.first_page
current_page.display_page()

# inturrupt that jumps between lists when the control is pushed
def select():
    global current_page
    global mylcd
    if current_page.jump:
        current_page = current_page.jump
        current_page.display_page()

# inturrupt that moves up and down the Menu objects when control turned
def turn_page():
    global current_page
    global mylcd
    if channel2.value == 1:
        if current_page.get_prev_page() == None:
            pass
        else:
            current_page = current_page.get_prev_page()
            current_page.display_page()
    else:
        if current_page.get_next_page() == None:
            pass
        else:
            current_page = current_page.get_next_page()
            current_page.display_page()

# set the inturrupts
channel1.when_pressed = turn_page
push.when_pressed = select


# running loop that updates the sensors
while True:
    
    bus.write_byte(0x48, 0x1)
    sleep(.1)
    bus.read_byte(0x48)
    sleep(.1)
    pot =  bus.read_byte(0x48)
    print(f'pot = {pot}')
    sleep(2)

    bus.write_byte(0x48, 0x2)
    sleep(.1)
    bus.read_byte(0x48)
    sleep(.1)
    photo = bus.read_byte(0x48)
    print(f'photo = {photo}')
    sleep(2)

    bus.write_byte(0x48, 0x3)
    sleep(.1)
    bus.read_byte(0x48)
    sleep(.1)
    touch = bus.read_byte(0x48)
    print(f'touch = {touch}')
    sleep(2)