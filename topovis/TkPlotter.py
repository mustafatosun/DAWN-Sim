from .common import *
try:
    from Tkinter import *
except ImportError:  # could be Python3
    from tkinter import *
from . import GenericPlotter

arrowMap = { 'head' : LAST, 'tail' : FIRST, 'both' : BOTH, 'none' : NONE }

def colorStr(color):
    if color == None:
        return ''
    else:
        return '#%02x%02x%02x' % tuple(int(x*255) for x in color)

###############################################
class Plotter(GenericPlotter):
    def __init__(self, windowTitle='TopoVis', terrain_size=None, params=None):
        GenericPlotter.__init__(self, params)
        self.nodes = {}
        self.links = {}
        self.nodeLinks = {}
        self.lineStyles = {}
        self.shapes = {}
        self.windowTitle = windowTitle
        self.prepareCanvas(terrain_size)
        self.lastShownTime = 0

    ###################
    def prepareCanvas(self,terrain_size=None):
        if terrain_size is not None:
            tx,ty = terrain_size
        else:
            tx,ty = 700,700
        
        self.tk = Tk()
        self.tk.title(self.windowTitle)

        frame = Frame(self.tk, width=tx, height=ty)
        frame.pack(expand=True, fill=BOTH)

        ver_scrollbar = Scrollbar(frame, orient=VERTICAL)
        ver_scrollbar.pack(side=RIGHT, fill=Y)

        hor_scrollbar = Scrollbar(frame, orient=HORIZONTAL)
        hor_scrollbar.pack(side=BOTTOM, fill=X)
        
        scr_width = self.tk.winfo_screenwidth() * 2
        scr_height = self.tk.winfo_screenheight() * 2

        self.canvas = Canvas(frame, width=tx, height=ty, scrollregion=(0,0, scr_width, scr_height), yscrollincrement=10, xscrollincrement=10)  
        self.canvas.pack(expand=True, fill=BOTH, side=LEFT)

        ver_scrollbar.config(command=self.canvas.yview)
        hor_scrollbar.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=ver_scrollbar.set, xscrollcommand=hor_scrollbar.set)

        self.timeText = self.canvas.create_text(0,0,text="Time=0.0",anchor=NW)

    ###################
    def setTime(self, time):
        if (time - self.lastShownTime > 0.05):
            self.canvas.itemconfigure(self.timeText, text='Time: %.2fS' % time)
            self.lastShownTime = time

    ###################
    def updateNodePosAndSize(self,id):
        p = self.params
        c = self.canvas
        if id not in self.nodes.keys():
            node_tag = c.create_oval(0,0,0,0)
            label_tag = c.create_text(0,0,text=str(id))
            self.nodes[id] = (node_tag,label_tag)
        else:
            (node_tag,label_tag) = self.nodes[id]

        node = self.scene.nodes[id]
        nodesize = node.scale*p.nodesize
        x1 = node.pos[0] - nodesize
        y1 = node.pos[1] - nodesize
        (x2,y2) = (x1 + nodesize*2, y1 + nodesize*2)
        c.coords(node_tag, x1, y1, x2, y2)
        c.coords(label_tag, node.pos)

        for l in self.nodeLinks[id]:
            self.updateLink(*l)

    ###################
    def configLine(self,tagOrId,style):
        config = {}
        config['fill']  = colorStr(style.color)
        config['width'] = style.width
        config['arrow'] = arrowMap[style.arrow]
        config['dash']  = style.dash
        self.canvas.itemconfigure(tagOrId,**config)

    ###################
    def configPolygon(self,tagOrId,lineStyle,fillStyle):
        config = {}
        config['outline'] = colorStr(lineStyle.color)
        config['width']    = lineStyle.width
        config['dash']     = lineStyle.dash
        config['fill']     = colorStr(fillStyle.color)
        self.canvas.itemconfigure(tagOrId,**config)

    ###################
    def createLink(self,src,dst,style):
        if src is dst:
            raise('Source and destination are the same node')
        p = self.params
        c = self.canvas
        (x1,y1,x2,y2) = computeLinkEndPoints(
                self.scene.nodes[src],
                self.scene.nodes[dst], 
                p.nodesize)
        link_obj = c.create_line(x1, y1, x2, y2, tags='link')
        self.configLine(link_obj, self.scene.lineStyles[style])
        return link_obj

    ###################
    def updateLink(self,src,dst,style):
        p = self.params
        c = self.canvas
        link_obj = self.links[(src,dst,style)]
        (x1,y1,x2,y2) = computeLinkEndPoints(
                self.scene.nodes[src],
                self.scene.nodes[dst], 
                p.nodesize)
        c.coords(link_obj, x1, y1, x2, y2)


    ###################
    def node(self,id,x,y):
        self.nodeLinks[id] = []
        self.updateNodePosAndSize(id)
        self.tk.update()

    ###################
    def nodemove(self,id,x,y):
        self.updateNodePosAndSize(id)
        self.tk.update()

    ###################
    def nodecolor(self,id,r,g,b):
        (node_tag,label_tag) = self.nodes[id]
        self.canvas.itemconfig(node_tag, outline=colorStr((r,g,b)))
        self.canvas.itemconfigure(label_tag, fill=colorStr((r,g,b)))
        self.tk.update()

    ###################
    def nodewidth(self,id,width):
        (node_tag,label_tag) = self.nodes[id]
        self.canvas.itemconfig(node_tag, width=width)
        self.tk.update()

    ###################
    def nodescale(self,id,scale):
        # scale attribute has been set by TopoVis
        # just update the node
        self.updateNodePosAndSize(id)
        self.tk.update()

    ###################
    def nodelabel(self,id,label):
        (node_tag,label_tag) = self.nodes[id]
        self.canvas.itemconfigure(label_tag, text=self.scene.nodes[id].label)
        self.tk.update()

    ###################
    def addlink(self,src,dst,style):
        if style == 'edge' and src > dst:
            src, dst = dst, src
        self.nodeLinks[src].append((src,dst,style))
        self.nodeLinks[dst].append((src,dst,style))
        self.links[(src,dst,style)] = self.createLink(src, dst, style)
        self.tk.update()

    ###################
    def dellink(self,src,dst,style):
        if style == 'edge' and src > dst:
            src, dst = dst, src
        self.nodeLinks[src].remove((src,dst,style))
        self.nodeLinks[dst].remove((src,dst,style))
        self.canvas.delete(self.links[(src,dst,style)])
        del self.links[(src,dst,style)]
        self.tk.update()

    ###################
    def clearlinks(self):
        self.canvas.delete('link')
        self.links.clear()
        for n in self.nodes.keys():
            self.nodeLinks[n] = []
        self.tk.update()

    ###################
    def circle(self,x,y,r,id,linestyle,fillstyle):
        if id in self.shapes.keys():
            self.canvas.delete(self.shapes[id])
            del self.shapes[id]
        self.shapes[id] = self.canvas.create_oval(x-r,y-r,x+r,y+r)
        self.configPolygon(self.shapes[id], linestyle, fillstyle)
        self.tk.update()

    ###################
    def line(self,x1,y1,x2,y2,id,linestyle):
        if id in self.shapes.keys():
            self.canvas.delete(self.shapes[id])
            del self.shapes[id]
        self.shapes[id] = self.canvas.create_line(x1,y1,x2,y2)
        self.configLine(self.shapes[id], linestyle)
        self.tk.update()

    ###################
    def rect(self,x1,y1,x2,y2,id,linestyle,fillstyle):
        if id in self.shapes.keys():
            self.canvas.delete(self.shapes[id])
            del self.shapes[id]
        self.shapes[id] = self.canvas.create_rectangle(x1,y1,x2,y2)
        self.configPolygon(self.shapes[id], linestyle, fillstyle)
        self.tk.update()

    ###################
    def delshape(self,id):
        if id in self.shapes.keys():
            self.canvas.delete(self.shapes[id])
            self.tk.update()
