import math

# Constants
DEFAULT=-1
ENABLED=1
DISABLED=0
INF=1e38
NINF=-1e38

###############################################
class Color:
   def __init__(self,s):
      if type(s) is str:
         self.rgb = tuple(float(x) for x in s.split(','))
      elif type(s) is tuple:
         self.rgb = s

   def __getitem__(self,x):
      return self.rgb[x]

   def __str__(self):
      return ','.join(str(x) for x in self.rgb)

###############################################
class LineStyle(object):
    """
    Define a set of attributes for line drawing.  Attributes currently
    supported are
        - color: specifies color in (r,g,b) tuple, where 0 <= r,g,b <= 1
        - dash:  can be either one of the following formats, (), (s,),
          (s1,s2).  The first one results in a solid line; the second results
          in a line drawn with the length of s and skip for the same amount;
          the last will draw the line for the length of s1 and skip for s2.
          However, the actual behavior depends on the plotter.
        - width: speficies the width of the line
        - arrow: specifies how arrow heads are drawn.  Acceptable values are
          'head', 'tail', 'both', and 'none'.
    """
    def __init__(self, **kwargs):
        self.color = (0,0,0)
        self.dash = ()
        self.width = 1
        self.arrow = 'none'
        for (k,v) in kwargs.items():
            if k in ['color', 'dash', 'width', 'arrow']:
                setattr(self, k, v)
            else:
                raise Exception('Unknown option "%s"' % k)

    def __repr__(self):
        return '[color=%s,dash=%s,width=%s,arrow=%s]' % (
                self.color, self.dash, self.width, self.arrow)

###############################################
class FillStyle(object):
    """
    Define a set of attributes for shape filling.  The only attribute currently
    supported is 'color', which specifies color in (r,g,b) tuple, where 0 <=
    r,g,b <= 1
    """
    def __init__(self, **kwargs):
        self.color = None
        for (k,v) in kwargs.items():
            if k in ['color']:
                setattr(self, k, v)
            else:
                raise Exception('Unknown option "%s"' % k)

    def __repr__(self):
        return '[color=%s]' % self.color

###############################################
class TextStyle(object):
    """
    Define a set of attributes for text rendering.  Attributes currently
    supported are 'color', 'font', and 'size'.
    """
    def __init__(self, **kwargs):
        self.color = (0,0,0)
        for (k,v) in kwargs.items():
            if k in ['color', 'font', 'size']:
                setattr(self, k, v)
            else:
                raise Exception('Unknown option "%s"' % k)

###############################################
class Parameters:

   #########################
   def __init__(self):
      self.margin     = 72
      self.scale      = 1.0
      self.nodesize   = 10
      self.textsize   = 12
      self.hollow     = True
      self.double     = False
      self.nodewidth  = 1
      self.grid       = 0
      self.bgcolor    = Color('1.0,1.0,1.0')
      self.gridcolor  = Color('0.5,0.5,0.5')
      self.nodecolor  = Color('0.0,0.0,0.0')
      self.guard      = self.nodesize
      self.timescale  = 1


###############################################
def computeLinkEndPoints(src, dst, nodesize):
   "Computes both endpoints of a link to be drawn between src and dst"

   dx = dst.pos[0] - src.pos[0]
   dy = dst.pos[1] - src.pos[1]
   dist = math.sqrt(dx*dx + dy*dy);

   # Check if src and dst are on the exact same location
   if (dist == 0.0):
       return dst.pos[0],dst.pos[1],dst.pos[0],dst.pos[1]

   ux = dx/dist;
   uy = dy/dist;
   newsrcx = src.pos[0] + (ux * nodesize * src.scale);
   newsrcy = src.pos[1] + (uy * nodesize * src.scale);
   newdstx = dst.pos[0] - (ux * nodesize * dst.scale);
   newdsty = dst.pos[1] - (uy * nodesize * dst.scale);

   return (newsrcx, newsrcy, newdstx, newdsty)
