

import agx
import agxSDK
import agxCollide

from agxRender import Color
import agx_helper

import math

module_len = 0.0725
intermediate_len = 0.025
servo_shape = agx_helper.load_shape('assets/servo.obj')
bottom_shape = agx_helper.load_shape('assets/bottom.obj')
upper_shape = agx_helper.load_shape('assets/upper.obj')
intermediate_shape = agx_helper.load_shape('assets/intermediate.obj')

sensor_bounds = agx.Vec3(0.0085, 0.002, 0.02)
intermediate_bounds = agx.Vec3(0.0125, 0.0325, 0.0325)


class ModulePart(agx.RigidBody):

    def __init__(self, app: agx_helper.AgxApp):
        super().__init__()
        self.app = app  # type: agx_helper.AgxApp


class ModuleAssembly(agxSDK.Assembly):

    def __init__(self, app: agx_helper.AgxApp):
        super().__init__()
        self.app = app  # type: agx_helper.AgxApp


class IntermediatePart(ModuleAssembly):

    def __init__(self, app: agx_helper.AgxApp):
        super().__init__(app)

        visual_geometry = agxCollide.Geometry(intermediate_shape.deepCopy(),
                                              agx.AffineMatrix4x4.rotate(math.pi/2, 0, 1, 0) *
                                              agx.AffineMatrix4x4.rotate(math.pi, 1, 0, 0))
        visual_geometry.setEnableCollisions(False)
        app.create_visual(visual_geometry, Color.Orange())

        collision_geometry = agxCollide.Geometry(agxCollide.Box(intermediate_bounds),
                                                 agx.AffineMatrix4x4.translate(intermediate_len/2, 0, 0))

        self.body = agx.RigidBody()
        self.body.add(visual_geometry)
        self.body.add(collision_geometry)
        self.add(self.body)

        sensor_geometry = agxCollide.Geometry(agxCollide.Box(sensor_bounds),
                                              agx.AffineMatrix4x4.translate(intermediate_len/2, -0.035, 0))
        self.sensor = agx.RigidBody(sensor_geometry)
        self.add(self.sensor)

        self.merged_body = agx.MergedBody()
        self.merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.body, self.sensor))
        app.add(self.merged_body)


class BottomPart(ModulePart):

    def __init__(self, app: agx_helper.AgxApp):
        super().__init__(app)

        servo_geometry = agxCollide.Geometry(servo_shape.deepCopy())
        servo_geometry.setEnableCollisions(False)
        app.create_visual(servo_geometry, Color.Gray())

        bottom_geometry = agxCollide.Geometry(bottom_shape.deepCopy())
        bottom_geometry.setEnableCollisions(False)
        app.create_visual(bottom_geometry, Color.Black())

        self.add(servo_geometry)
        self.add(bottom_geometry)


class UpperPart(ModulePart):

    def __init__(self, app: agx_helper.AgxApp):
        super().__init__(app)

        upper_geometry = agxCollide.Geometry(upper_shape.deepCopy())
        upper_geometry.setEnableCollisions(False)
        app.create_visual(upper_geometry, Color.Black())

        self.add(upper_geometry)


class TypeA(ModuleAssembly):

    def __init__(self, app: agx_helper.AgxApp):
        super().__init__(app)

        self.len = 0

        self.intermediate = IntermediatePart(app)
        self.intermediate.setPosition(agx.Vec3(-module_len / 2 - intermediate_len, 0, 0))

        self.bottom = BottomPart(app)

        self.add(self.intermediate)
        self.add(self.bottom)

        merged_body = self.intermediate.merged_body
        merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.intermediate.body, self.bottom))
        app.add(merged_body)


class TypeB(ModuleAssembly):

    def __init__(self, app: agx_helper.AgxApp):
        super().__init__(app)

        self.len = module_len + intermediate_len

        self.upper = UpperPart(app)

        self.intermediate = IntermediatePart(app)
        self.intermediate.setPosition(agx.Vec3(module_len / 2, 0, 0))

        self.bottom = BottomPart(app)
        self.bottom.setPosition(agx.Vec3(module_len + intermediate_len, 0, 0))

        self.add(self.upper)
        self.add(self.intermediate)
        self.add(self.bottom)

        merged_body = self.intermediate.merged_body
        merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.upper, self.intermediate.body))
        merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.intermediate.body, self.bottom))
        app.add(merged_body)


class TypeC(ModuleAssembly):

    def __init__(self, app: agx_helper.AgxApp):
        super().__init__(app)

        self.upper = UpperPart(app)
        self.intermediate = IntermediatePart(app)
        self.intermediate.setPosition(agx.Vec3(module_len / 2, 0, 0))

        self.add(self.upper)
        self.add(self.intermediate)

        merged_body = self.intermediate.merged_body
        merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.upper, self.intermediate.body))
        app.add(merged_body)


class Snake(ModuleAssembly):

    def __init__(self, app: agx_helper.AgxApp, num_servos: int=2):
        super().__init__(app)

        self.servos = []  # type: list[agx.Hinge]
        self.sensors = []  # type: list[agx.RigidBody]

        def connect(rb1: agx.RigidBody, rb2: agx.RigidBody):
            axis = agx.Vec3(0, 0, -1)
            pos = agx.Vec3(0.0, 0.007, 0)
            hinge = agx_helper.create_constraint(
                pos=pos, axis=axis, c=agx.Hinge, rb1=rb1, rb2=rb2)  # type: agx.Hinge
            hinge.setCompliance(1E-10)
            hinge.getMotor1D().setEnable(True)
            hinge.getLock1D().setEnable(False)
            self.add(hinge)
            self.servos.append(hinge)

        last_part = None  # type: ModulePart
        for i in range(0, num_servos):

            if i == 0:
                type_a = TypeA(app)
                type_b = TypeB(app)
                type_b.setPosition(type_a.len, 0, 0)
                self.add(type_a)
                self.add(type_b)
                connect(type_a.bottom, type_b.upper)
                self.sensors.append(type_a.intermediate.sensor)
                self.sensors.append(type_b.intermediate.sensor)
                last_part = type_b
            elif i == num_servos-1:
                type_b = last_part  # type: TypeB
                type_c = TypeC(app)
                type_c.setPosition(type_b.getPosition().x() + type_b.len, 0, 0)
                self.add(type_c)
                connect(type_b.bottom, type_c.upper)
                self.sensors.append(type_c.intermediate.sensor)
                last_part = type_c
            else:
                type_b1 = last_part  # type: TypeB
                type_b2 = TypeB(app)
                type_b2.setPosition(type_b1.getPosition().x() + type_b1.len, 0, 0)
                self.add(type_b2)
                connect(type_b1.bottom, type_b2.upper)
                self.sensors.append(type_b2.intermediate.sensor)
                last_part = type_b2

        self.num_servos = len(self.servos)
        self.num_sensors = len(self.sensors)

        print(self.sensors)

    def get_contacts(self, contacts=[]) -> list:
        contacts.clear()
        for sensor in self.sensors:  # type: agx.RigidBody
            c = self.app.get_contacts(sensor)
            contacts.append(c)
        return contacts


###########################
def add_floor(app: agx_helper.AgxApp):

    size = agx.Vec3(25, 25, 0.1)
    floor = agxCollide.Geometry(agxCollide.Box(size))
    floor.setPosition(0, 0, -size.z()/2)
    app.create_visual(floor, Color.Green())
    app.add(floor)


class SineMotion(agxSDK.StepEventListener):

    def __init__(self, snake: Snake, servo_index: int):
        super().__init__(agxSDK.StepEventListener.PRE_STEP)

        self.snake = snake

        period = 2
        f = 1/period
        self.omega = 2 * math.pi * f
        self.amplitude = math.radians(45)

        t = (1/(snake.num_servos-2)) * servo_index
        v0 = 0
        v1 = math.pi*2

        self.phase = (1-t) * v0 + t * v1
        print("servo{} phase={}".format(servo_index, math.degrees(self.phase)))

        self.hinge = snake.servos[servo_index]

    def pre(self, time):
        speed = self.amplitude * math.sin(self.omega * time + self.phase)
        self.hinge.getMotor1D().setSpeed(-speed)

        # c = self.snake.get_contacts()[0]
        # if c is not None:
        #     for p in c:  # type: agxCollide.ContactPoint
        #         print(p.getDepth())





def build_scene():

    app = agx_helper.AgxApp(2)
    app.create_sky()
    add_floor(app)

    snake = Snake(app, 5)
    snake.setRotation(agx.EulerAngles(math.pi/2, 0, 0))
    snake.setPosition(agx.Vec3(0, 0, 0.1))
    app.add(snake)

    for i in range(0, snake.num_servos):
        app.add_event_listener(SineMotion(snake, i))

    app.init_camera(eye=agx.Vec3(-1, -1, 0.5))
