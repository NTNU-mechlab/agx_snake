
import agx
import agxOSG
import agxModel
import agxCollide

from agxRender import Color

import math

from snake import SnakeApp
from snake.snake_module import Snake
from snake.snake_module import SineMotion


class Terrain:

    def __init__(self, app: SnakeApp):

        hf = agxCollide.HeightField.createFromFile("assets/textures/dirtRoad128.png", 6, 6, -0.5, 0.5)
        terrain = agxModel.Terrain(hf)
        app.add(terrain)

        self.material = agx.Material("GroundMaterial")

        terrain_data = terrain.getDataInterface()  # type: agxModel.TerrainDataInterface
        terrain_data.setMaxCompressionMultiplier(32)
        particle_adhesion = 0
        deformability = 100
        angle_of_repose = math.pi * 0.2
        material_index = 0
        terrain_data.add(self.material, material_index, particle_adhesion, deformability, angle_of_repose)

        range_for_youngs_modulus = agx.RangeReal(10000, 20000)
        terrain_renderer = agxOSG.TerrainRenderer(terrain, range_for_youngs_modulus, app.root)
        app.add(terrain_renderer)

        terrain_visual = terrain_renderer.getTerrainNode()
        agxOSG.setDiffuseColor(terrain_visual, Color(0.7, 0.7, 0.8, 1))
        agxOSG.setSpecularColor(terrain_visual, Color(0.4, 0.4, 0.4, 1))
        agxOSG.setShininess(terrain_visual, 128)


def build_scene():

    app = SnakeApp()
    app.create_sky()

    terrain = Terrain(app)

    snake = Snake(app, 6)
    snake.setRotation(agx.EulerAngles(math.pi / 2, 0, 0))
    snake.setPosition(agx.Vec3(0, .5, 0.3))
    app.add(snake)

    terrain_snake_cm = app.sim.getMaterialManager() \
        .getOrCreateContactMaterial(terrain.material, snake.material)  # type: agx.ContactMaterial
    terrain_snake_cm.setFrictionCoefficient(3)
    terrain_snake_cm.setUseContactAreaApproach(True)
    terrain_snake_cm.setYoungsModulus(3E3)

    fm = agx.IterativeProjectedConeFriction(agx.FrictionModel.DIRECT)
    terrain_snake_cm.setFrictionModel(fm)

    for i in range(0, snake.num_servos):
        app.add_event_listener(SineMotion(snake, i))

    app.init_camera(eye=agx.Vec3(-2, -2, 1), center=agx.Vec3(0, 0, 0.5))
