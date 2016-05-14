#!/usr/bin/env python
from perlin import FractalNoise
import Image
import ImageDraw
from time import time
from subprocess import call


start_time = time()

IMG_LOCATION = 'perlin.png'
IMG_SIZE = (128, 128)

#create file
img = Image.new('RGB', IMG_SIZE)

#draw it
r1 = FractalNoise(seed='pineapple', iterations=2)

draw = ImageDraw.Draw(img)
for x in range(0, IMG_SIZE[0]):
    for y in range(0, IMG_SIZE[1]):
        #red = p2[(x, y)]
        red = r1[(x, y)]
        green = 0  # (g1[(x, y)] + g2[(x, y)]) / 2
        blue = 0  # (b1[(x, y)] + b2[(x, y)]) / 2
        draw.point((x, y), fill=(red, green, blue))


del draw

#save it
img.save(IMG_LOCATION)

#open it
call(['open', IMG_LOCATION])

print 'Time elapsed: %i seconds' % (time() - start_time)
