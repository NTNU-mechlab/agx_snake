
import agx
import agxOSG
import agxModel
import agxCollide

from agxRender import Color

import math

import snakeapp
from snakeapp.snake_with_intermediates import Snake
from snakeapp.snake_with_intermediates import ExampleSineMotion


class Terrain:

    def __init__(self):

        hf = agxCollide.HeightField.createFromFile("assets/textures/dirtRoad128.png", 6, 6, -0.5, 0.5)
        terrain = agxModel.Terrain(hf)
        snakeapp.add(terrain)

        self.material = agx.Material("GroundMaterial")

        terrain_data = terrain.getDataInterface()  # type: agxModel.TerrainDataInterface
        terrain_data.setMaxCompressionMultiplier(32)
        particle_adhesion = 0
        deformity = 100
        angle_of_repose = math.pi * 0.2
        material_index = 0
        terrain_data.add(self.material, material_index, particle_adhesion, deformity, angle_of_repose)

        range_for_youngs_modulus = agx.RangeReal(10000, 20000)
        terrain_renderer = agxOSG.TerrainRenderer(terrain, range_for_youngs_modulus, snakeapp.root())
        snakeapp.add(terrain_renderer)

        terrain_visual = terrain_renderer.getTerrainNode()
        agxOSG.setDiffuseColor(terrain_visual, Color(0.7, 0.7, 0.8, 1))
        agxOSG.setSpecularColor(terrain_visual, Color(0.4, 0.4, 0.4, 1))
        agxOSG.setShininess(terrain_visual, 128)


def build_scene():

    snakeapp.create_sky()

    snake = Snake(6)
    snake.setRotation(agx.EulerAngles(math.pi / 2, 0, 0))
    snake.setPosition(agx.Vec3(0, .5, 0.3))
    snakeapp.add(snake)

    terrain = Terrain()

    terrain_snake_cm = snakeapp.sim().getMaterialManager() \
        .getOrCreateContactMaterial(terrain.material, snake.material)  # type: agx.ContactMaterial
    terrain_snake_cm.setFrictionCoefficient(3)
    terrain_snake_cm.setUseContactAreaApproach(True)
    terrain_snake_cm.setYoungsModulus(3E3)

    fm = agx.IterativeProjectedConeFriction(agx.FrictionModel.DIRECT)
    terrain_snake_cm.setFrictionModel(fm)

    for i in range(0, snake.num_servos):
        snakeapp.add_event_listener(ExampleSineMotion(snake, i))

    snakeapp.init_camera(eye=agx.Vec3(-2, -2, 1), center=agx.Vec3(0, 0, 0.5))

    import agxSDK

    class ReadSensor(agxSDK.StepEventListener):
        def __init__(self):
            super().__init__(agxSDK.StepEventListener.POST_STEP)

        def post(self, time):
            for i in range(0, snake.num_sensors):
                print("Sensor{} force={}".format(i, snakeapp.get_sum_force_magnitude(snake.sensors[i])))
            print("")

    snakeapp.add_event_listener(ReadSensor())


