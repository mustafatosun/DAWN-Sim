import sys
sys.path.insert(1, '.')
from source import DawnSimVis


###########################################################
# Override required functions
class Node(DawnSimVis.BaseNode):

    ###################
    def init(self):
        pass

    ###################
    def run(self):
        pass

    ###################
    def on_receive(self, pck):
        pass

    ###################
    def finish(self):
        pass


# create a Simulator object
sim = DawnSimVis.Simulator(
    duration=100,
    timescale=1,
    visual=True,
    terrain_size=(650, 650),
    title='Blank Template')

# add nodes here

# start the simulation
sim.run()
