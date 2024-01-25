# ---------- Imports ----------#
import os
import bpy
import math

from SEDcreator import SEDcreator_createCluster
from SEDcreator import SEDcreator_utils
from SEDcreator import SEDcreator_setupClasses
from SEDcreator import SEDcreator_renderClasses

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
        pan_col2 = layout.column()
        pan_col3 = layout.column()
        pan_col1.label(text="Scene Management")
        pan_col2.label(text="Delimitations")
        pan_col3.label(text="Setup cameras")
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

        row = pan_col1.row()
        layout.separator()

        row2 = pan_col2.row()
        row2.prop(setupProp, 'x_min')
        row2 = pan_col2.row()
        row2.prop(setupProp, 'x_max')
        row2 = pan_col2.row()
        row2.prop(setupProp, 'y_min')
        row2 = pan_col2.row()
        row2.prop(setupProp, 'y_max')
        row2 = pan_col2.row()
        row2.prop(setupProp, 'z_min')
        row2 = pan_col2.row()
        row2.prop(setupProp, 'z_max')

        row2 = pan_col2.row()
        layout.separator()

        row3 = pan_col3.row()
        row3.operator('object.sed_setup')

        if context.scene.RenderProperties.renderReady:

            layout.separator()

            pan_col4 = layout.column()
            pan_col4.label(text="Render Management")

            renderProp = context.scene.RenderProperties
            row4 = pan_col4.row()
            row4.prop(renderProp, "bool_albedo")
            row4 = pan_col4.row()
            row4.prop(renderProp, "bool_depth")
            row4 = pan_col4.row()
            row4.prop(renderProp, "bool_normal")
            row4 = pan_col4.row()
            row4.prop(renderProp, "bool_id")
            row4 = pan_col4.row()
            row4.prop(renderProp, "bool_beauty")
            row4 = pan_col4.row()
            row4.prop(renderProp, "bool_roughness")
            row4 = pan_col4.row()
            row4.prop(renderProp, "bool_curvature")
            row4 = pan_col4.row()
            row4.prop(renderProp, "bool_transmission")
            row4 = pan_col4.row()
            row4.prop(renderProp, "exportFolder")
            row4 = pan_col4.row()
            row4.prop(renderProp, "start")
            row4 = pan_col4.row()
            row4.prop(renderProp, "end")
            row4 = pan_col4.row()
            row4.operator('object.sed_render')
        else:
            row = layout.row()
            row.label(text="Render not ready")


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

classes = [sedPanel, SettingsOperator, InfoAdd]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.InfoAdd = bpy.props.PointerProperty(type=InfoAdd)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.InfoAdd


if __name__ == "__main__":
    register()
