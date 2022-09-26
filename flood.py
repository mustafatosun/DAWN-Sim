import random
import sys
sys.path.insert(1, '.')
from source import DawnSim

SOURCE = 0


###########################################################
class Node(DawnSim.BaseNode):

    ###################
    def init(self):
        self.flood_received = False

    ###################
    def run(self):
        if self.id == SOURCE:
            pck = {'example_variable': 5}
            self.cb_flood_send(pck)
            self.flood_received = True

    ###################
    def on_receive(self, pck):
        if not self.flood_received:
            self.log('Flood msg is received first time.')
            self.set_timer(1, self.cb_flood_send, pck)
            self.flood_received = True

    ###################
    def cb_flood_send(self, pck):
        self.send(DawnSim.BROADCAST_ADDR, pck)
        self.log('Flood msg is sent.')


# setting the simulation
sim = DawnSim.Simulator(
    duration=10,
    timescale=1)

# adding nodes
sim.add_node(Node, (50,50), 75)
sim.add_node(Node, (50,100), 75)
sim.add_node(Node, (50,150), 75)
sim.add_node(Node, (100,150), 75)

# start the simulation
sim.run()
