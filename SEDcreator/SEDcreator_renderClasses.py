import os
import bpy

from SEDcreator import SEDcreator_utils
from SEDcreator import SEDcreator_renderUtils

class RenderProperties(bpy.types.PropertyGroup):
    renderReady: bpy.props.BoolProperty(name="Toggle Option")
    exportFolder: bpy.props.StringProperty(
        name="Export Folder", description="Relative export folder", default="img")

    # Render map type management
    bool_albedo: bpy.props.BoolProperty(name="Albedo",
                                        description="Render albedo map",
                                        default=True
                                         )
    bool_depth: bpy.props.BoolProperty(name="Depth",
                                       description="Render depth map",
                                       default=True
                                        )
    bool_normal: bpy.props.BoolProperty(name="Normal",
                                        description="Render normal map",
                                        default=True
                                         )
    bool_id: bpy.props.BoolProperty(name="Id",
                                    description="Render id map",
                                    default=True
                                     )
    bool_beauty: bpy.props.BoolProperty(name="Beauty",
                                        description="Beauty render",
                                        default=True
                                         )
    bool_transmission: bpy.props.BoolProperty(name="Transmission",
                                              description="Transmission mask",
                                              default=True
                                               )
    bool_roughness: bpy.props.BoolProperty(name="Roughness",
                                              description="Roughness mask",
                                              default=True
                                              )
    bool_curvature: bpy.props.BoolProperty(name="Curvature",
                                              description="Curvature mask",
                                              default=True
                                              )
    start: bpy.props.IntProperty(name="FirstFrame", default=0)

    end: bpy.props.IntProperty(name="LastFrame", default=1)

class RenderOperator(bpy.types.Operator):
    bl_idname = "object.sed_render"
    bl_label = "Start Render"
    bl_description = "Start render with the set parameters. Please, open the console to be able to follow the rendering."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.RenderProperties.renderReady == True

    def execute(self, context):

        renderProp = context.scene.RenderProperties
        #il ne faut plus qu'on ait cette condition
        #if (renderProp.bool_beauty and (renderProp.bool_roughness or renderProp.bool_curvature)) or (renderProp.bool_roughness and (renderProp.bool_beauty or renderProp.bool_curvature)) or (renderProp.bool_curvature and (renderProp.bool_beauty or renderProp.bool_roughness)):
            #self.report({'ERROR'}, "You can only select once between Beauty, Roughness and Curvature")
        # Get the img folder path
        filePath = bpy.data.filepath
        curDir = os.path.dirname(filePath)
        imgDir = os.path.join(
            curDir, context.scene.RenderProperties.exportFolder)

        # Create the img folder if it does not exist
        os.makedirs(imgDir, exist_ok=True)

        # Get the dome shape
        domeShape = context.scene.SetupProperties.domeShape

        # ----------- GET OBJECTS -----------#

        #faire le renumber ici
        #origin = bpy.context.scene.objects['Cameras']

        SEDcreator_utils.renumberSEDCameras()
        sedCameras = SEDcreator_utils.getSEDCameras()
        #camerasObjs = [context.scene.objects[f'Camera_{nCam}'] for nCam in
        #          range(context.scene.RenderProperties.start, context.scene.RenderProperties.end + 1)]
        camerasObjs = sedCameras[renderProp.start:renderProp.end + 1]

        print("---------- Rendering start ----------")

        # ----------- PRE-RENDER -----------#
        #origin.rotation_euler[2] = 0

        SEDcreator_renderUtils.launchRender(context, camerasObjs, imgDir)
        #SEDcreator_renderUtils.launchRender("Roughness", context, camerasObjs, imgDir)
        #SEDcreator_renderUtils.launchRender("Curvature", context, camerasObjs, imgDir)
        print("rendering end")

        return {'FINISHED'}

classes = [RenderProperties, RenderOperator]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.RenderProperties = bpy.props.PointerProperty(type=RenderProperties)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.RenderProperties


if __name__ == "__main__":
    register()
