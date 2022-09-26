"""Visualisation of wsnsimpy library. Based on wsnsimpy_tk.
"""
from source import DawnSim
from source.DawnSim import *
from threading import Thread
from topovis import Scene
from topovis.TkPlotter import Plotter


class BaseNode(DawnSim.BaseNode):
    """Class to model a visualised network node inherited DawnSim.Node.

       Attributes:
           scene (Scene): Scene object to visualise

    """

    ###################
    def __init__(self, sim, id, pos, tx_range):
        """Constructor for visualised Node class. Creates a node in topovis scene.

           Args:
               sim (Simulator): Simulation environment of node.
               id (int): Global unique ID of node.
               pos (Tuple(double,double)): Position of node.
               tx_range (double): Transmission range of node.

           Returns:
               BaseNode: Created node object.
        """
        super().__init__(sim, id, pos, tx_range)
        self.scene = self.sim.scene
        self.scene.node(id, *pos)

    ###################
    def send(self, dest, pck):
        """Visualise sending process in addition to base send method.

           Args:
                pck (Dict): Package to be sent.
                dest (int): Destination address (node id)

           Returns:

        """
        obj_id = self.scene.circle(
            self.pos[0], self.pos[1],
            self.tx_range,
            line="wsnsimpy:tx")
        super().send(dest, pck)
        self.delayed_exec(0.2, self.scene.delshape, obj_id)

        if not dest == DawnSim.BROADCAST_ADDR:
            destPos = self.sim.nodes[dest].pos
            if distance(self.pos, destPos) <= self.tx_range:
                obj_id = self.scene.line(
                    self.pos[0], self.pos[1],
                    destPos[0], destPos[1],
                    line="wsnsimpy:unicast")
                self.delayed_exec(0.2,self.scene.delshape,obj_id)

    ###################
    def move_step(self):
        """Visualise move process in addition to base move method.

           Args:

           Returns:

        """
        super().move_step()
        self.scene.nodemove(self.id, self.pos[0], self.pos[1])

    ###################
    def sleep(self):
        """Make invisible.

           Args:

           Returns:

        """
        for (dist, node) in self.neighbor_distance_list:
            if dist <= self.tx_range:
                self.scene.dellink(self.id, node.id, "edge")
            else:
                break
        self.change_color(0.9411, 0.9411, 0.9411)
        super().sleep()

    ###################
    def change_color(self, r, g, b):
        """Change node's color.

           Args:
               r (double): red value between 0 and 1
               g (double): green value between 0 and 1
               b (double): blue value between 0 and 1

           Returns:

        """
        self.scene.nodecolor(self.id, r, g, b)


###########################################################
class _FakeScene:
    def _fake_method(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return self._fake_method


###########################################################


###########################################################
class Simulator(DawnSim.Simulator):
    '''Wrap WsnSimPy's Simulator class so that Tk main loop can be started in the
    main thread

    Attributes:
        visual (bool): A flag to visualising process.
        terrain_size (Tuple(double,double)): Size of visualised terrain.
    '''

    def __init__(self, duration, timescale=1, seed=0, terrain_size=(650, 650), visual=True, title=None):
        """Constructor for visualised Simulator class.

           Args:
               duration (double): Duration of simulation.
               timescale (double): Seconds in real time for 1 second in simulation. It arranges speed of simulation
               seed (double): seed for Random bbject.
               terrain_size (Tuple(double,double)): Size of visualised terrain.
               visual (bool): A flag to visualising process.
               title (string): Title of scene.

           Returns:
               Simulator: Created Simulator object.
        """
        super().__init__(duration, timescale, seed)
        self.visual = visual
        self.terrain_size = terrain_size
        if self.visual:
            self.scene = Scene(realtime=True)
            self.scene.linestyle("wsnsimpy:tx", color=(0, 0, 1), dash=(5, 5))
            self.scene.linestyle("wsnsimpy:ack", color=(0, 1, 1), dash=(5, 5))
            self.scene.linestyle("wsnsimpy:unicast", color=(0, 0, 1), width=3, arrow='head')
            self.scene.linestyle("wsnsimpy:collision", color=(1, 0, 0), width=3)
            self.scene.linestyle("prev", color=(0,.8,0), arrow="tail", width=2)
            self.scene.linestyle("edge", color=(.7,.7,.7), width=1)
            if title is None:
                title = "WsnSimPy"
            self.tkplot = Plotter(windowTitle=title, terrain_size=terrain_size)
            self.tk = self.tkplot.tk
            self.scene.addPlotter(self.tkplot)
            self.scene.init(*terrain_size)
        else:
            self.scene = _FakeScene()

    def _update_time(self):
        """Updates time in scene.

           Args:

           Returns:
        """
        while True:
            self.scene.setTime(self.now)
            yield self.timeout(0.1)

    def update_neighbor_list(self, id):
        """Updates edges in scene.

           Args:
               id (int): Global unique id of node
           Returns:
        """
        node1 = self.nodes[id]
        for (dist, node2) in node1.neighbor_distance_list:
            if dist <= node1.tx_range:
                try:
                   self.scene.dellink(id, node2.id, "edge")
                except:
                    pass
            else:
                break
        super().update_neighbor_list(id)
        for (dist, node2) in node1.neighbor_distance_list:
            if dist <= node1.tx_range:
                self.scene.addlink(id, node2.id, "edge")
            else:
                break


    def run(self):
        """Starts visualisation process. Puts base run method to a Thread so that visualisation become main process.

           Args:

           Returns:
        """
        if self.visual:
            self.env.process(self._update_time())
            thr = Thread(target=super().run)
            thr.setDaemon(True)
            thr.start()
            self.tkplot.tk.mainloop()
        else:
            super().run()
