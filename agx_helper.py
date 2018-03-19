
import agx
import agxSDK
import agxUtil
import agxPython
import agxCollide

import agxIO
import agxOSG
import agxRender

import sys


class AgxApp:
    
    def __init__(self, num_threads=2):

        self.customData = dict()
        self.sim = agxPython.getContext().environment.getSimulation()  # type: agxSDK.Simulation
        self.app = agxPython.getContext().environment.getApplication()  # type: agxOSG.ExampleApplication
        self.root = agxPython.getContext().environment.getSceneRoot()  # type: agxOSG.Group
        agx.setNumThreads(num_threads)

    def add_event_listener(self, listener):
        self.sim.addEventListener(listener)

    def add(self, *objects):
        for obj in objects:
            self.sim.add(obj)

    def create_visual(self, obj, diffuse_color=None, ambient_color=None, shininess=None, alpha=None):
        return create_visual(obj, self.root, diffuse_color, ambient_color, shininess, alpha)

    def init_camera(self, eye=agx.Vec3(-25, -25, 25), center=agx.Vec3(), up=agx.Vec3.Z_AXIS()):
        self.app.setCameraHome(eye, center, up)

    def get_contacts(self, body: agx.RigidBody):
        return get_contacts(body, self.sim.getSpace())

    def create_sky(self):
        c1 = agxRender.Color.SkyBlue()
        c2 = agxRender.Color.DodgerBlue()

        def to_vec3(o: agxRender.Color):
            return agx.Vec3(o.x(), o.y(), o.z())

        self.app.getSceneDecorator().setBackgroundColor(to_vec3(c1), to_vec3(c2))

    def register_additional_scenes(self, *additional_scenes):
        if len(additional_scenes) > 0:
            
            def add_scene(name):
                scene_key = self.app.getNumScenes()+1
                self.app.addScene(script_file_name, name, ord(ascii(scene_key)), True)
            
            script_file_name = self.app.getArguments().getArgumentName(1)
            script_file_name=script_file_name.replace('agxscene:','')
            print(script_file_name)
            
            for scene in additional_scenes:
                add_scene(scene)


class KeyEvent(agxSDK.GuiEventListener):

    def __init__(self, key, func):
        super().__init__(agxSDK.GuiEventListener.KEYBOARD)
        self.key = key
        self.func = func

    def keyboard(self, key, alt, x, y, down):
        handled = False
        if key == self.key:
            self.func()
            handled = True
        return handled


def load_model(path) -> agxCollide.Geometry:
    return agxCollide.Geometry(load_shape(path))


def load_shape(path) -> agxCollide.Trimesh:
    return agxUtil.createTrimeshFromFile(
                        path, agxCollide.Trimesh.REMOVE_DUPLICATE_VERTICES, agx.Matrix3x3())


def create_visual(obj, root, diffuse_color: agxRender.Color=None, ambient_color: agxRender.Color=None,
                  shininess=None, alpha: float=None):

    node = agxOSG.createVisual(obj, root)
        
    if diffuse_color is not None:
        agxOSG.setDiffuseColor(node, diffuse_color)
        
    if ambient_color is not None:
        agxOSG.setAmbientColor(node, ambient_color)
        
    if shininess is not None:
        agxOSG.setShininess(node, shininess)
        
    if alpha is not None:
        agxOSG.setAlpha(node, alpha)
        
    return node


def get_contacts(body: agx.RigidBody, space: agxCollide.Space) -> list:

    contacts = []
    for gc in space.getGeometryContacts():  # type: agxCollide.GeometryContact
        if not gc.isEnabled():
            continue
        rb1 = gc.rigidBody(0)  # type: agx.RigidBody
        rb2 = gc.rigidBody(1)  # type: agx.RigidBody

        if rb1 is not None and rb1.getUuid() != body.getUuid() and rb2 is not None and rb2.getUuid() != body.getUuid():
            continue
        points = gc.points()  # type: agxCollide.ContactPointVector
        for point in points:  # type: agxCollide.ContactPoint
            if not point.getEnabled():
                continue
            contacts.append(point)

    return contacts


def create_constraint(**kwds):
    
    pos = None
    if 'pos' in kwds:
        pos = kwds['pos']
    else:
        pos = agx.Vec3()
        
    axis = None
    if 'axis' in kwds:
        axis = kwds['axis']
    else:
        axis = agx.Vec3.Z_AXIS()

    c = kwds['c']
    rb1 = kwds['rb1']
    rb2 = kwds['rb2']

    f1 = agx.Frame()
    f2 = agx.Frame()
    
    agx.Constraint.calculateFramesFromBody(pos, axis, rb1, f1, rb2, f2)
    return c(rb1, f1, rb2, f2)


if agxPython.getContext() is None:
    init = agx.AutoInit()
    
    argParser = agxIO.ArgumentParser([sys.executable] + sys.argv)
    
    app = agxOSG.ExampleApplication()
    app.addScene(argParser.getArgumentName(1), "build_scene", ord('1'), True)
    
    if app.init(argParser):
        app.run()
    else:
        print("An error occurred while initializing ExampleApplication.")