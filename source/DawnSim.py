"""Simulator library for MANETs.
Based on wsnsimpy library.
Author: Mustafa Tosun
"""

import bisect
import inspect
import random
import simpy
from simpy.util import start_delayed
from source import config

BROADCAST_ADDR = config.BROADCAST_ADDR
"""double: Keeps broadcast address.
"""


###########################################################
def ensure_generator(env, func, *args, **kwargs):
    """
    Make sure that func is a generator function.  If it is not, return a
    generator wrapper
    """
    if inspect.isgeneratorfunction(func):
        return func(*args, **kwargs)
    else:
        def _wrapper():
            func(*args, **kwargs)
            yield env.timeout(0)

        return _wrapper()


###########################################################
def distance(pos1, pos2):
    """Calculates the distance between two positions.

       Args:
           pos1 (Tuple(double,double)): First position.
           pos2 (Tuple(double,double)): Second position.

       Returns:
           double: returns the distance between two positions.
    """
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5


###########################################################
class BaseNode:
    """Class to model a network node with basic operations. It's base class for more complex node classes.

       Attributes:
           pos (Tuple(double,double)): Position of node.
           tx_range (double): Transmission range of node.
           sim (Simulator): Simulation environment of node.
           id (int): Global unique ID of node.
           timers (List of Timer): Keeps timers set by node
           is_sleeping (bool): If it is True, It means node is sleeping and can not receive messages.
           Otherwise, node is awaken.
           logging (bool): It is a flag for logging. If it is True, nodes outputs can be seen in terminal.
           neighbor_distance_list (List of Tuple(double,Node)): Sorted list of nodes distances to other nodes.
            Each Tuple keeps a distance and a node id.
           timeout (Function): timeout function

    """

    ############################
    def __init__(self, sim, id, pos, tx_range):
        """Constructor for base Node class.

           Args:
               sim (Simulator): Simulation environment of node.
               id (int): Global unique ID of node.
               pos (Tuple(double,double)): Position of node.
               tx_range (double): Transmission range of node.

           Returns:
               Node: Created node object.
        """
        self.pos = pos
        self.tx_range = tx_range
        self.sim = sim
        self.id = id
        self.timers = []
        self.is_sleeping = False
        self.logging = True
        self.neighbor_distance_list = []
        self.timeout = self.sim.timeout

    ############################
    def __repr__(self):
        """Representation method of Node.

           Args:

           Returns:
               string: represents Node object as a string.
        """
        return '<Node %d:(%.2f,%.2f)>' % (self.id, self.pos[0], self.pos[1])

    ###################
    def __lt__(self, other):
        """Compares the object wth other object.

           Args:
               other(BaseNode): the other object to compare

           Returns:
               bool: returns True if the object's id is less than the other object's id.
        """
        if self.id < other.id:
            return True
        else:
            return False

    ############################
    @property
    def now(self):
        """Property for time of simulation.

           Args:

           Returns:
               double: Time of simulation.
        """
        return self.sim.env.now

    ############################
    def log(self, msg):
        """Writes outputs of node to terminal.

           Args:
                msg (string): Output text
           Returns:

        """
        if self.logging:
            print(f"Node {'#' + str(self.id):4}[{self.now:10.5f}] {msg}")

    ############################
    def send(self, dest, pck):
        """Sends given package. If dest address is broadcast address, it sends the package to all neighbors.

           Args:
                pck (Dict): Package to be sent. It should contain 'dest' which is destination address.
                dest (int): Destination address (node id)
           Returns:

        """
        for (dist, node) in self.neighbor_distance_list:
            if dist <= self.tx_range:
                if dest == BROADCAST_ADDR or dest == node.id:
                    if config.SIM_MESSAGGING_DELAY_TYPE == 'prop':
                        prop_time = dist / 3000000
                    elif config.SIM_MESSAGGING_DELAY_TYPE == 'random':
                        prop_time = random.random()
                    else:
                        prop_time = config.SIM_MESSAGGING_CONSTANT_DELAY
                    self.delayed_exec(prop_time, node.on_receive_check, pck)
            else:
                break

    ############################
    def set_timer(self, delay, callback, *args, **kwargs):
        """Sets a timer with a given name. It appends name of timer to the active timer list.

           Args:
                delay (double): Duration of timer.
                callback (function): callback function of timer.
                *args (string): Additional args.
                **kwargs (string): Additional key word args.
           Returns:
               timer: A Timer object

        """
        timer = Timer(self.sim.env, delay, callback, *args, **kwargs)
        self.timers.append(timer)
        return timer

    ############################
    def kill_all_timers(self):
        """Kills node's all timers.

           Args:

           Returns:


        """
        for timer in self.timers:
            timer.kill()

    ############################
    def delayed_exec(self, delay, func, *args, **kwargs):
        """Executes a function with given parameters after a given delay.

           Args:
                delay (double): Delay duration.
                func (Function): Function to execute.
                *args (double): Function args.
                delay (double): Function key word args.
           Returns:

        """
        return self.sim.delayed_exec(delay, func, *args, **kwargs)

    ############################
    def init(self):
        """Initialize a node. It is executed at the beginning of simulation. It should be overridden if needed.

           Args:

           Returns:

        """
        pass

    ############################
    def run(self):
        """Run method of a node. It is executed after init() at the beginning of simulation.
        It should be overridden if needed.

           Args:

           Returns:

        """
        pass

    ###################
    def move_step(self):
        """Moves one step from the current position towards target position

           Args:
.
           Returns:
         """
        step_size = config.SIM_MOVE_STEP_TIME * self.speed
        if distance(self.pos, self.target_pos) <= step_size:
            self.pos = self.target_pos
        else:
            target_ratio = step_size / distance(self.pos, self.target_pos)
            self.pos = (self.pos[0] + (self.target_pos[0] - self.pos[0]) * target_ratio,
                        self.pos[1] + (self.target_pos[1] - self.pos[1]) * target_ratio)
        self.sim.update_neighbor_list(self.id)
        if self.pos != self.target_pos:
            self.delayed_exec(config.SIM_MOVE_STEP_TIME, self.move_step)

    ###################
    def move(self, target_pos, speed):
        """Changes the target position to given position

           Args:
               target_pos (tuple of double): target position.
               speed (double): speed
.
           Returns:
         """
        self.target_pos = target_pos
        self.speed = speed
        self.delayed_exec(config.SIM_MOVE_STEP_TIME, self.move_step)

    ############################
    def on_receive(self, pck):
        """It is executed when node receives a package. It should be overridden if needed.

           Args:
                pck (Dict): Package received
           Returns:

        """
        pass

    ############################
    def on_receive_check(self, pck):
        """Checks if node is sleeping or not for incoming package.
        If sleeping, does not call on_recieve() and does not receive package.

           Args:
                pck (Dict): Incoming package
           Returns:

        """
        if not self.is_sleeping:
            self.on_receive(pck)

    ############################
    def sleep(self):
        """Make node sleep. In sleeping node can not receive packages.

           Args:

           Returns:

        """
        self.is_sleeping = True

    ############################
    def wake_up(self):
        """Wake node up to receive incoming messages.

           Args:

           Returns:

        """
        self.is_sleeping = False

    ############################
    def finish(self):
        """It is executed at the end of simulation. It should be overridden if needed.

           Args:

           Returns:

        """
        pass


###########################################################
class Timer(object):
    """
    Class to model timers.
    """

    def __init__(self, env, delay, callback, *args, **kwargs):
        self.env = env
        self.delay = delay
        self.action = None
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.canceled = False
        self.set()

    def run(self):
        """
        Calls a callback after time has elapsed.
        """
        try:
            yield self.env.timeout(self.delay)
            self.callback(*self.args, **self.kwargs)
        except simpy.Interrupt as i:
            self.canceled = True

    def set(self):
        """
        Starts the timer
        """
        if not self.action:
            self.action = self.env.process(self.run())

    def kill(self):
        """
        Kills the timer
        """
        if self.action:
            self.action.interrupt()
            self.action = None

    def reset(self):
        """
        Interrupts the current timer and restarts.
        """
        self.kill()
        self.set()


###########################################################
class Simulator:
    """Class to model a network.

       Attributes:
           env (simpy.rt.RealtimeEnvironment): Environment object in simpy
           timescale (double): Seconds in real time for 1 second in simulation. It arranges speed of simulation
           nodes (List of Node): Nodes in network.
           duration (double): Duration of simulation.
           random (Random): Random object to use.
           timeout (Function): Timeout Function.

    """

    ############################
    def __init__(self, duration, timescale=1, seed=0):
        """Constructor for Simulator class.

           Args:
               until (double): Duration of simulation.
               timescale (double): Seconds in real time for 1 second in simulation. It arranges speed of simulation
               seed (double): seed for Random bbject.

           Returns:
               Simulator: Created Simulator object.
        """
        self.env = simpy.rt.RealtimeEnvironment(factor=timescale, strict=False)
        self.nodes = []
        self.duration = duration
        self.timescale = timescale
        self.random = random.Random(seed)
        self.timeout = self.env.timeout

    ############################
    @property
    def now(self):
        """Property for time of simulation.

           Args:

           Returns:
               double: Time of simulation.
        """
        return self.env.now

    ############################
    def delayed_exec(self, delay, func, *args, **kwargs):
        """Executes a function with given parameters after a given delay.

           Args:
                delay (double): Delay duration.
                func (Function): Function to execute.
                *args (double): Function args.
                delay (double): Function key word args.
           Returns:

        """
        func = ensure_generator(self.env, func, *args, **kwargs)
        start_delayed(self.env, func, delay=delay)

    ############################
    def add_node(self, node_class, pos, tx_range):
        """Adds a new node in to network.

           Args:
                nodeclass (Class): Node class inherited from Node.
                pos (Tuple(double,double)): Position of node.
           Returns:
                nodeclass object: Created nodeclass object
        """
        id = len(self.nodes)
        node = node_class(self, id, pos, tx_range)
        self.nodes.append(node)
        self.update_neighbor_list(id)
        return node

    ############################
    def update_neighbor_list(self, id):
        '''
        Maintain each node's neighbor list by sorted distance after affected
        by addition or relocation of node with ID id

        Args:
            id (int): Global unique id of node
        Returns:

        '''
        me = self.nodes[id]

        # (re)sort other nodes' neighbor lists by distance
        for n in self.nodes:
            # skip this node
            if n is me:
                continue

            nlist = n.neighbor_distance_list

            # remove this node from other nodes' neighbor lists
            for i, (dist, neighbor) in enumerate(nlist):
                if neighbor is me:
                    del nlist[i]
                    break

            # then insert it while maintaining sort order by distance
            bisect.insort(nlist, (distance(n.pos, me.pos), me))

        self.nodes[id].neighbor_distance_list = [
            (distance(n.pos, me.pos), n)
            for n in self.nodes if n is not me
        ]
        self.nodes[id].neighbor_distance_list.sort()

    ############################
    def run(self):
        """Runs the simulation. It initialize every node, then executes each nodes run function.
        Finally calls finish functions of nodes.

           Args:

           Returns:

        """
        for n in self.nodes:
            n.init()
        for n in self.nodes:
            self.env.process(ensure_generator(self.env, n.run))
        self.env.run(until=self.duration)
        for n in self.nodes:
            n.finish()
