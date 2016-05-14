import random
from math import cos, pi, log, ceil


class PerlinNoise(object):
    def __init__(self, **kwargs):
        self.size = kwargs.pop('size', (64, 64))
        self.seed = kwargs.pop('seed', 'melon')
        self.interpolate_func = kwargs.pop('interpolate', 'linear')
        self.gridvalues = None
        self.xrange = None
        self.yrange = None

    def calcGridValue(self, x, y):
        #print 'calcGridValue(%i, %i)' % (x, y)
        random.seed(str(x) + str(y) + self.seed)
        return random.randint(0, 255)

    def expand_x(self, x):
        import pdb; pdb.set_trace()  # XXX BREAKPOINT
        if x > self.xrange[1]:  # append values to the left
            #print 'expand_x -(%i)' % x
            for yy in range(self.yrange[0], self.yrange[1] + 1):
                self.gridvalues[yy] += [self.calcGridValue(xx, yy)
                                        for xx in range(self.xrange[1], x + 1)]
            self.xrange[1] = x
        elif x < self.xrange[0]:  # append values to the right
            #print 'expand_x (%i)-' % x
            for yy in range(self.yrange[0], self.yrange[1] + 1):
                self.gridvalues[yy] = ([self.calcGridValue(xx, yy)
                                        for xx in range(x, self.xrange[0])] +
                                       self.gridvalues[yy])
            self.xrange[0] = x

    def expand_y(self, y):
        if y > self.yrange[1]:  # appand values to the top
            #print 'expand_y -(%i)' % y
            for yy in range(self.yrange[1] + 1, y + 1):
                self.gridvalues += [[self.calcGridValue(xx, yy)
                                    for xx in range(self.xrange[0],
                                                    self.xrange[1] + 1)]]
            self.yrange[1] = y
        elif y < self.yrange[0]:  # append values to the bottom
            #print 'expand_y (%i)-' % y
            for yy in range(y, self.yrange[0]):
                self.gridvalues = ([[self.calcGridValue(xx, yy)
                                    for xx in range(self.xrange[0],
                                                    self.xrange[1] + 1)]] +
                                   self.gridvalues)
            self.yrange[0] = y

    def getgridvalue(self, x, y):
        #print 'getgridvalue', x, y
        if self.xrange is None:
            self.xrange = [x, x]
            self.yrange = [y, y]
            self.gridvalues = [[self.calcGridValue(x, y)]]
        self.expand_x(x)
        self.expand_y(y)
        r = self.gridvalues[y - self.yrange[0] - 1][x - self.xrange[0] - 1]
        #print 'returned', r
        return r

    def __getitem__(self, xy):
        return self.getvalue(xy)

    def getvalue(self, xy, size=None):
        if size is None:
            size = self.size
        x, y = xy
        bl_corner = [x / size[0],
                     y / size[1]]
        corners = [(bl_corner[0] + dx, bl_corner[1] + dy)
                   for dx in (0, 1)
                   for dy in (0, 1)]  # corners are in order: bl, tl, br, tr

        values = []
        #print 'corners', corners
        for idx, corner in enumerate(corners):
            values.append(self.getgridvalue(corner[0], corner[1]))

        #interpolate between values
        ptile_rel = ([float(xy[a]) / size[a] - bl_corner[a]
                     for a in (0, 1)])
        interpol_h = [self.interpolate(values[n], values[n + 2], ptile_rel[0])
                      for n in (0, 1)]
        return int(self.interpolate(interpol_h[0],
                                    interpol_h[1],
                                    ptile_rel[1]))

    def interpolate(self, a, b, x):
        """Interpolate x between a and b where the distance a-b == 1"""
        if self.interpolate_func == 'linear':
            return (1 - x) * a + x * b
        elif self.interpolate_func == 'cosine':
            f = (1 - cos(x * pi)) * 0.5
            return a * (1 - f) + b * f
        else:
            raise Exception('No interpolation function found')


class FractalNoise(PerlinNoise):
    def __init__(self, **kwargs):
        super(FractalNoise, self).__init__(**kwargs)
        self.persistency = kwargs.pop('persistency', .5)
        self.iterations = int(ceil(log(1 / float(min(self.size)),
                                       self.persistency)))
        if ('iterations' in kwargs
                and kwargs['iterations'].__class__.__name__ == 'int'
                and kwargs['iterations'] <= self.iterations):
            self.iterations = kwargs.pop('iterations')
        self.octaves = [tuple([tuple([int(self.size[d] *
                                      self.persistency ** iteration)
                                      for d in range(2)]),
                              self.persistency ** iteration])
                        for iteration in range(self.iterations + 1)]

    def getvalue(self, xy):
        a1 = [super(FractalNoise, self).getvalue(xy, size) *
              persistance
              for size, persistance in self.octaves]
        a2 = [p for size, p in self.octaves]
        #print self.octaves
        #print a1
        #print a2
        return int(sum(a1) / sum(a2))
