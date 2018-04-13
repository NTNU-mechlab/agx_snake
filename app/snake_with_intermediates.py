
import agx
import agxSDK
import agxCollide
import agxRender

import math

import app

module_len = 0.0725
intermediate_len = 0.025
servo_shape = app.load_shape('assets/servo.obj')
bottom_shape = app.load_shape('assets/bottom.obj')
upper_shape = app.load_shape('assets/upper.obj')
intermediate_shape = app.load_shape('assets/intermediate.obj')

sensor_bounds = agx.Vec3(0.0085, 0.002, 0.02)
intermediate_bounds = agx.Vec3(0.013, 0.0325, 0.0325)


class IntermediatePart(agxSDK.Assembly):

    def __init__(self, material: agx.Material=None):
        super().__init__()

        visual_geometry = agxCollide.Geometry(intermediate_shape.deepCopy(),
                                              agx.AffineMatrix4x4.rotate(math.pi/2, 0, 1, 0) *
                                              agx.AffineMatrix4x4.rotate(math.pi, 1, 0, 0))
        visual_geometry.setEnableCollisions(False)
        app.create_visual(visual_geometry, agxRender.Color.Orange())

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

        if material is not None:
            collision_geometry.setMaterial(material)
            sensor_geometry.setMaterial(material)

        self.merged_body = agx.MergedBody()
        self.merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.body, self.sensor))
        app.add(self.merged_body)


class BottomPart(agx.RigidBody):

    def __init__(self):
        super().__init__()

        servo_geometry = agxCollide.Geometry(servo_shape.deepCopy())
        servo_geometry.setEnableCollisions(False)
        app.create_visual(servo_geometry, agxRender.Color.Gray())

        bottom_geometry = agxCollide.Geometry(bottom_shape.deepCopy())
        bottom_geometry.setEnableCollisions(False)
        app.create_visual(bottom_geometry, agxRender.Color.Black())

        self.add(servo_geometry)
        self.add(bottom_geometry)


class UpperPart(agx.RigidBody):

    def __init__(self):
        super().__init__()

        upper_geometry = agxCollide.Geometry(upper_shape.deepCopy())
        upper_geometry.setEnableCollisions(False)
        app.create_visual(upper_geometry, agxRender.Color.Black())

        self.add(upper_geometry)


class TypeA(agxSDK.Assembly):

    def __init__(self, material: agx.Material=None):
        super().__init__()

        self.len = 0

        self.intermediate = IntermediatePart(material)
        self.intermediate.setPosition(agx.Vec3(-module_len / 2 - intermediate_len, 0, 0))

        self.bottom = BottomPart()

        self.add(self.intermediate)
        self.add(self.bottom)

        merged_body = self.intermediate.merged_body
        merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.intermediate.body, self.bottom))
        app.add(merged_body)


class TypeB(agxSDK.Assembly):

    def __init__(self, material: agx.Material=None):
        super().__init__()

        self.len = module_len + intermediate_len

        self.upper = UpperPart()

        self.intermediate = IntermediatePart(material)
        self.intermediate.setPosition(agx.Vec3(module_len / 2, 0, 0))

        self.bottom = BottomPart()
        self.bottom.setPosition(agx.Vec3(module_len + intermediate_len, 0, 0))

        self.add(self.upper)
        self.add(self.intermediate)
        self.add(self.bottom)

        merged_body = self.intermediate.merged_body
        merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.upper, self.intermediate.body))
        merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.intermediate.body, self.bottom))
        app.add(merged_body)


class TypeC(agxSDK.Assembly):

    def __init__(self, material: agx.Material=None):
        super().__init__()

        self.len = (module_len*0.5) + intermediate_len

        self.upper = UpperPart()
        self.intermediate = IntermediatePart(material)
        self.intermediate.setRotation(agx.EulerAngles(math.pi, 0, math.pi))
        self.intermediate.setPosition(agx.Vec3(module_len/2 + intermediate_len, 0, 0))

        self.add(self.upper)
        self.add(self.intermediate)

        merged_body = self.intermediate.merged_body
        merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.upper, self.intermediate.body))
        app.add(merged_body)


class Snake(agxSDK.Assembly):

    def __init__(self, num_servos: int=2):
        super().__init__()

        self.servos = []  # type: list[agx.Hinge]
        self.sensors = []  # type: list[agx.RigidBody]

        self.material = agx.Material("snake_material_{}".format(self.getUuid().__str__))

        self.len = 0

        def connect(rb1: agx.RigidBody, rb2: agx.RigidBody):
            axis = agx.Vec3(0, 0, -1)
            pos = agx.Vec3(0.0, 0.007, 0)
            hinge = app.create_constraint(
                pos=pos, axis=axis, c=agx.Hinge, rb1=rb1, rb2=rb2)  # type: agx.Hinge
            hinge.setCompliance(1E-12)
            hinge.getMotor1D().setEnable(True)
            hinge.getMotor1D().setCompliance(1E-12)
            hinge.getLock1D().setEnable(False)
            hinge.getRange1D().setEnable(True)
            hinge.getRange1D().setRange(-math.pi/2, math.pi)
            self.add(hinge)
            self.servos.append(hinge)

        def add(part):
            self.len += part.len
            self.add(part)

        last_part = None  # type: agx.RigidBody
        for i in range(0, num_servos):

            if i == 0:
                type_a = TypeA(self.material)
                type_b = TypeB(self.material)
                type_b.setPosition(type_a.len, 0, 0)
                add(type_a)
                add(type_b)
                connect(type_a.bottom, type_b.upper)
                self.sensors.append(type_a.intermediate.sensor)
                self.sensors.append(type_b.intermediate.sensor)
                last_part = type_b
            elif i == num_servos-1:
                type_b = last_part  # type: TypeB
                type_c = TypeC(self.material)
                type_c.setPosition(type_b.getPosition().x() + type_b.len, 0, 0)
                add(type_c)
                connect(type_b.bottom, type_c.upper)
                self.sensors.append(type_c.intermediate.sensor)
                last_part = type_c
            else:
                type_b1 = last_part  # type: TypeB
                type_b2 = TypeB(self.material)
                type_b2.setPosition(type_b1.getPosition().x() + type_b1.len, 0, 0)
                add(type_b2)
                connect(type_b1.bottom, type_b2.upper)
                self.sensors.append(type_b2.intermediate.sensor)
                last_part = type_b2

        self.num_servos = len(self.servos)
        self.num_sensors = len(self.sensors)

    def get_contacts(self, contacts: list=[]) -> list:
        contacts.clear()
        for sensor in self.sensors:  # type: agx.RigidBody
            c = app.get_contacts(sensor)
            contacts.append(c)
        return contacts

    def get_force_magnitude_at(self, intermediate_index):
        return app.get_sum_force_magnitude(self.sensors[intermediate_index])

    def set_hinge_compliance(self, compliance):
        for servo in self.servos:
            servo.getMotor1D().setCompliance(compliance)


class ExampleSineMotion(agxSDK.StepEventListener):

    def __init__(self, snake: Snake, servo_index: int):
        super().__init__(agxSDK.StepEventListener.PRE_STEP)

        self.snake = snake

        self._omega = None
        self.set_period(2)

        self.amplitude = math.radians(35)

        t = (1/(snake.num_servos-2)) * servo_index
        self.v0 = 0
        self.v1 = math.pi*2

        self._phase = (1-t) * self.v0 + t * self.v1
        print("servo{} phase={}".format(servo_index, math.degrees(self._phase)))

        self.hinge = snake.servos[servo_index]

    def get_period(self):
        return self._period

    def set_period(self, period: float):
        f = 1 / period
        self._omega = 2 * math.pi * f

    def pre(self, time):
        speed = self.amplitude * math.sin(self._omega * time + self._phase)
        self.hinge.getMotor1D().setSpeed(speed)

    period = property(get_period, set_period)
