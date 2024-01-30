import os
import bpy

from SEDcreator import SEDcreator_createCluster
from SEDcreator import SEDcreator_utils


class SetupOperator(bpy.types.Operator):
    bl_idname = "object.sed_setup"
    bl_label = "Set Project Setup"
    bl_description = "Setup the scene with all the selected empty objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        self.createSEDCollections(context)

        for obj in selected:
            if obj.type == 'EMPTY':
                SEDcreator_createCluster.create(context, obj)
                self.linkEmptyToCollection(obj, context)

        context.scene.RenderProperties.renderReady = True  # Set rendering Ready
        return {'FINISHED'}

    def linkEmptyToCollection(self, object, context):
        if context.scene.SetupProperties.domeShape == 'I':
            self.linkObjectHierarchyToCollection(object, context, "IcoSEDCollection")
        elif context.scene.SetupProperties.domeShape == 'SI':
            self.linkObjectHierarchyToCollection(object, context, "SemiIcoSEDCollection")
        elif context.scene.SetupProperties.domeShape == 'U':
            self.linkObjectHierarchyToCollection(object, context, "SphereSEDCollection")
        else:
            self.linkObjectHierarchyToCollection(object, context, "SemiSphereSEDCollection")

    def linkObjectHierarchyToCollection(self, object, context, collectionName):
        children = object.children_recursive
        for child in children:
            context.scene.collection.objects.unlink(child)
            bpy.data.collections[collectionName].objects.link(child)
        context.scene.collection.objects.unlink(object)
        bpy.data.collections[collectionName].objects.link(object)

    def collectionExists(self, context, collectionName):
        collections = context.scene.collection.children
        for collection in collections:
            if collection.name == collectionName:
                return True
        return False

    def createSEDCollections(self, context):
        if not self.collectionExists(context, "IcoSEDCollection"):
            icoCollection = bpy.data.collections.new("IcoSEDCollection")
            context.scene.collection.children.link(icoCollection)
        if not self.collectionExists(context, "SemiIcoSEDCollection"):
            semiIcoCollection = bpy.data.collections.new("SemiIcoSEDCollection")
            context.scene.collection.children.link(semiIcoCollection)
        if not self.collectionExists(context, "SphereSEDCollection"):
            sphereCollection = bpy.data.collections.new("SphereSEDCollection")
            context.scene.collection.children.link(sphereCollection)
        if not self.collectionExists(context, "SemiSphereSEDCollection"):
            semiSphereCollection = bpy.data.collections.new("SemiSphereSEDCollection")
            context.scene.collection.children.link(semiSphereCollection)

class SetupProperties(bpy.types.PropertyGroup):

    renderReady: bpy.props.BoolProperty(name="Toggle Option")
    domeShape: bpy.props.EnumProperty(name='Camera Dome Shape', description='Choose the shape of the camera dome',
                                      items={
                                          ('I', 'Icosahedron',
                                            'Place the cameras along the vertices of an Icosahedron'),
                                          ('SI', 'Semi Icosahedron',
                                            'Place the cameras along the vertices of a Icosahedron dome'),
                                          ('U', 'UV Sphere',
                                           'Place the cameras along the vertices of an UV Sphere'),
                                          ('SS', 'Semi Sphere',
                                          'Place the cameras along the vertices of a dome')
                                         # ('AI', 'Adaptative Icosahedron',
                                         #  'Place the cameras along the vertices of a Icosahedron dome that is limited by the bounding box'),
                                         # ('AS', 'Adaptative UV Sphere',
                                         #  'Place the cameras along the vertices of a UV Sphere that is limited by the bounding box')
                                      }, default='I')

    orientationCameras: bpy.props.EnumProperty(name="Cameras Orientation",
                                       description="Inward or outward orientation of cameras",
                                       items={
                                               ('I', 'Inward', 'Orient cameras inward'),
                                               ('O', 'Outward', 'Orient cameras outward'),
                                               ('F', 'Focus', 'Orient cameras to focus on the selectionned object'),
                                             }, default='I')

    clusterRadius: bpy.props.FloatProperty(name="Radius of the cluster",
                                          description="Radius of the cluster of cameras", default=1,
                                          min=0, max=10)  # In meters

    # - Icosahedron and Semi Icosahedron
    nbSubdiv: bpy.props.IntProperty(name="Number of Subdivisions", description="Number of dome shape's subdivisions",
                                    default=1, min=1, max=3, step=1)

    # - UV Sphere and Semi Sphere
    nbSegment: bpy.props.IntProperty(name="Number of segments", description="Number of sphere's rings", default=16,
                                     min=3, max=32, step=1)
    nbRing: bpy.props.IntProperty(name="Number of rings", description="Number of sphere's rings", default=8, min=3,
                                  max=16, step=1)
    x_max: bpy.props.FloatProperty(name="x maximum", description="Maximum x coordinate where cameras are displayed", default=100, min=-1000, max=1000, step=1)
    x_min: bpy.props.FloatProperty(name="x minimum", description="Minimum x coordinate where cameras are displayed", default=-100, min=-1000, max=1000, step=1)
    y_max: bpy.props.FloatProperty(name="y maximum", description="Maximum y coordinate where cameras are displayed", default=100, min=-1000, max=1000, step=1)
    y_min: bpy.props.FloatProperty(name="y minimum", description="Minimum y coordinate where cameras are displayed", default=-100, min=-1000, max=1000, step=1)
    z_max: bpy.props.FloatProperty(name="z maximum", description="Maximum z coordinate where cameras are displayed", default=100, min=-1000, max=1000, step=1)
    z_min: bpy.props.FloatProperty(name="z minimum", description="Minimum z coordinate where cameras are displayed", default=-100, min=-1000, max=1000, step=1)


classes = [SetupOperator, SetupProperties]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.SetupProperties = bpy.props.PointerProperty(type=SetupProperties)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.SetupProperties


if __name__ == "__main__":
    register()

