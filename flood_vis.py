import random
import sys
sys.path.insert(1, '.')
from source import DawnSimVis

SOURCE = 0


###########################################################
class Node(DawnSimVis.BaseNode):

    ###################
    def init(self):
        self.flood_received = False

    ###################
    def run(self):
        if self.id == SOURCE:
            self.change_color(1, 0, 0)
            pck = {'example_variable': 5}
            self.cb_flood_send(pck)
            self.flood_received = True

    ###################
    def on_receive(self, pck):
        if not self.flood_received:
            self.log('Flood msg is received first time.')
            self.change_color(0, 0, 1)
            self.set_timer(1, self.cb_flood_send, pck)
            self.flood_received = True

    ###################
    def cb_flood_send(self, pck):
        self.send(DawnSimVis.BROADCAST_ADDR, pck)
        self.log('Flood msg is sent.')


###########################################################
def create_network():
    # place nodes over 100x100 grids
    for x in range(10):
        for y in range(10):
            px = 50 + x*60 + random.uniform(-20,20)
            py = 50 + y*60 + random.uniform(-20,20)
            sim.add_node(Node, pos=(px,py), tx_range=75)


# setting the simulation
sim = DawnSimVis.Simulator(
    duration=100,
    timescale=1,
    visual=True,
    terrain_size=(650, 650),
    title='Flooding')

# creating network
create_network()

# start the simulation
sim.run()
