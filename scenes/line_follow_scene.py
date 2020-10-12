import agx
import agxOSG
import math
import agxUtil
from agxRender import Color

import snakeapp

TWO_PHI = 2 * math.pi


def build_scene():

    spline = agxUtil.CPCatmullRomBSpline()
    for t in range(0, 20, 2):
        y = 2 * math.sin(TWO_PHI * 0.1 * t)
        spline.add(agxUtil.SplinePoint(agx.Vec3(y, t, 1)))

    renderer = agxOSG.SplineRenderer(spline, snakeapp.root())
    renderer.setColor(Color.Red())

    snakeapp.sim().add(renderer)
