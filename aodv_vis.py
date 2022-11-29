import random
import sys
sys.path.insert(1, '.')
from source import DawnSimVis

SOURCE = 0
DEST = 99


###########################################################
class Node(DawnSimVis.BaseNode):

    ###################
    def init(self):
        self.prev = None

    ###################
    def run(self):
        if self.id == SOURCE:
            self.change_color(1, 0, 0)
            self.seq_no = 0
            package = {'type': 'RREQ', 'source': self.id}
            self.send(DawnSimVis.BROADCAST_ADDR, package)
            self.log(f'Started to find path to {DEST}')
        elif self.id == DEST:
            self.change_color(1, 0, 0)
        else:
            self.change_color(.7, .7, .7)

    ###################
    def on_receive(self, pck):
        if pck['type'] == 'RREQ':
            if self.prev is not None: return
            self.log(f"RREQ received first time from {pck['source']}")
            self.prev = pck['source']
            self.scene.addlink(self.prev, self.id, "prev")
            if self.id != DEST and self.id != SOURCE:
                self.change_color(0, .7, 0)
                self.set_timer(.5, self.timer_rreq_cb)
            elif self.id == DEST:
                self.set_timer(.5, self.timer_rreply_cb)
        elif pck['type'] == 'RREPLY':
            self.log(f"RREPLY received from {pck['source']}")
            self.next = pck['source']
            if self.id == SOURCE:
                self.set_timer(2, self.timer_start_data_cb)
            else:
                self.set_timer(.5, self.timer_rreply_cb)
        elif pck['type'] == 'DATA':
            if self.id != DEST:
                self.set_timer(.2, self.timer_forward_data_cb, pck['seq_no'])
            self.log(f"{pck['seq_no']}'th data received")

    ###################
    def timer_rreq_cb(self):
        package = {'type': 'RREQ', 'source': self.id}
        self.send(DawnSimVis.BROADCAST_ADDR, package)
        self.log('RREQ sent')

    ###################
    def timer_rreply_cb(self):
        package = {'type': 'RREPLY', 'source': self.id}
        self.send(self.prev, package)
        self.log('RREPLY sent')

    ###################
    def timer_start_data_cb(self):
        package = {'type': 'DATA', 'source': self.id, 'seq_no': self.seq_no}
        self.seq_no += 1
        self.send(self.next, package)
        self.log(f"Started to sent {self.seq_no}'th data")
        self.set_timer(1, self.timer_start_data_cb)

    ###################
    def timer_forward_data_cb(self, seq_no):
        package = {'type': 'DATA', 'source': self.id, 'seq_no': seq_no}
        self.send(self.next, package)
        self.log(f"{seq_no}'th data forwarded")


###########################################################
def create_network():
    # place nodes over 100x100 grids
    for x in range(10):
        for y in range(10):
            px = 50 + x * 60 + random.uniform(-20, 20)
            py = 50 + y * 60 + random.uniform(-20, 20)
            sim.add_node(Node, pos=(px, py), tx_range=75)


# setting the simulation
sim = DawnSimVis.Simulator(
    duration=100,
    timescale=1,
    visual=True,
    terrain_size=(650, 650),
    title='AODV')

# creating network
create_network()

# start the simulation
sim.run()
