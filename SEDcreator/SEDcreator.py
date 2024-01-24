# ---------- Imports ----------#
import os
import bpy
import math

from SEDcreator import createCluster
from SEDcreator import utils

#définir un xmax, xmin, etc que l'utilisateur entrera et les sphères seront dessinées de manière à être dans cet espace

#-------- Panel --------#
class sedPanel(bpy.types.Panel):
    bl_idname = 'SEDCREATOR_PT_sedcreator'
    bl_label = 'SEDcreator Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SEDcreator"

    def draw(self, context):
        layout = self.layout
        setupProp = context.scene.SetupProperties
        domeShape = setupProp.domeShape

        pan_col1 = layout.column()
        pan_col1.label(text="Scene Management")
        row = pan_col1.row()
        row.operator('object.sed_settings')
        row = pan_col1.row()
        row.prop(setupProp,
                 "domeShape")  # Dome shape parameter
        row = pan_col1.row()
        row.prop(setupProp, 'orientationCameras')
        row = pan_col1.row()
        row.prop(setupProp, 'clusterRadius')
        if domeShape == "I" or domeShape == "SI":
            row = pan_col1.row()
            row.prop(setupProp, "nbSubdiv")
        if domeShape == "U" or domeShape == "SS":
            row = pan_col1.row()
            row.prop(setupProp, "nbSegment")
            row = pan_col1.row()
            row.prop(setupProp, "nbRing")

        layout.separator()

        row = pan_col1.row()
        row.operator('object.sed_setup')
#       if setupProp.renderReady:
#
#           layout.separator()
#
#           pan_col3 = layout.column()
#           pan_col3.label(text="Render Management")
#
#           row = pan_col3.row()
#           row.prop(setupProp, "bool_albedo")
#           row = pan_col3.row()
#           row.prop(setupProp, "bool_depth")
#           row = pan_col3.row()
#           row.prop(setupProp, "bool_normal")
#           row = pan_col3.row()
#           row.prop(setupProp, "bool_id")
#           row = pan_col3.row()
#           row.prop(setupProp, "bool_beauty")
#           row = pan_col3.row()
#           row.prop(setupProp, "bool_roughness")
#           row = pan_col3.row()
#           row.prop(setupProp, "bool_curvature")
#           row = pan_col3.row()
#           row.prop(setupProp, "bool_transmission")
#           row = pan_col3.row()
#           row.prop(setupProp, "exportFolder")
#           row = pan_col3.row()
#           row.prop(setupProp, "start")
#           row = pan_col3.row()
#           row.prop(setupProp, "end")
#           row = pan_col3.row()
#           row.operator('object.scanrig_render')
#       else:
#           row = layout.row()
#           row.label(text="Render not ready")

# ---------- Project settings ----------#
class SettingsOperator(bpy.types.Operator):
    bl_idname = "object.sed_settings"
    bl_label = "Set Project Settings"
    bl_description = "Set the project settings corresponding to the FSCAM_CU135 cameras"
    bl_options = {'REGISTER', 'UNDO'}
    
#   tileSize ne nous concerne pas car on est à la 4.0(faudra voir si ça change des choses si on le rajoute)
    if bpy.app.version < (3, 0, 0):
        tileSize: bpy.props.IntProperty(name="Tiles Size", description="Size of the rendering tiles", default=256,
                                        min=64, max=1024, step=32)
    renderSamplesNumber: bpy.props.IntProperty(name="Samples", description="Number of samples for rendering",
                                               default=128, min=16, max=1024, step=16)

    def execute(self, context):

        # Useful variables
        rdr = context.scene.render
        cle = context.scene.cycles

        rdr.engine = 'CYCLES'
        cle.device = 'GPU'
        cle.samples = self.renderSamplesNumber
        cle.caustics_reflective = False
        cle.caustics_refractive = False

        rdr.resolution_x = 4208
        rdr.resolution_y = 3120

        if bpy.app.version < (3, 0, 0):
            rdr.tile_x = self.tileSize
            rdr.tile_y = self.tileSize

        # World settings
        context.scene.world.use_nodes = False
        context.scene.world.color = (0, 0, 0)

        return {'FINISHED'}

class InfoAdd(bpy.types.PropertyGroup):
    camNumber: bpy.props.IntProperty(name = "Number of cameras in the whole scanrig collections")

class SetupOperator(bpy.types.Operator):
    bl_idname = "object.sed_setup"
    bl_label = "Set Project Setup"
    bl_description = "Setup the scene with all the selected empty objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        for obj in selected:
            if obj.type == 'EMPTY':
                createCluster.create(context, obj)
        return {'FINISHED'}



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
    x_max: bpy.props.FloatProperty(name="x maximum", description="Maximum x coordinate where cameras are displayed", default=100, min=-1000, max=1000, step=1)
    x_max: bpy.props.FloatProperty(name="x maximum", description="Maximum x coordinate where cameras are displayed", default=100, min=-1000, max=1000, step=1)
    x_max: bpy.props.FloatProperty(name="x maximum", description="Maximum x coordinate where cameras are displayed", default=100, min=-1000, max=1000, step=1)
    x_max: bpy.props.FloatProperty(name="x maximum", description="Maximum x coordinate where cameras are displayed", default=100, min=-1000, max=1000, step=1)
    x_max: bpy.props.FloatProperty(name="x maximum", description="Maximum x coordinate where cameras are displayed", default=100, min=-1000, max=1000, step=1)


classes = [sedPanel, SettingsOperator, InfoAdd, SetupOperator, SetupProperties]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.SetupProperties = bpy.props.PointerProperty(type=SetupProperties)
    bpy.types.Scene.InfoAdd = bpy.props.PointerProperty(type=InfoAdd)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.SetupProperties
    del bpy.types.Scene.InfoAdd


if __name__ == "__main__":
    register()
