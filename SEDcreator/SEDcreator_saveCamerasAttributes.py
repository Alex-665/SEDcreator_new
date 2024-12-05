import bpy
import os
import numpy as np
from SEDcreator import SEDcreator_utils


class SaveCamerasAttributesOperator(bpy.types.Operator):
    bl_idname = "object.sed_save_cameras_attributes"
    bl_label = "Save Cameras Attributes"
    bl_description = "Go through all cameras created with this add-on and save their location, angle and focal length to a .npz file"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.RenderProperties.renderReady == True # on le met quand meme car s'il n'y a pas de cameras ca sert a rien

    def execute(self, context):
        # Get the img folder path
        renderProp = context.scene.RenderProperties
        filePath = bpy.data.filepath
        curDir = os.path.dirname(filePath)
        imgDir = os.path.join(curDir, renderProp.exportFolder)

        # Create the img folder if it does not exist
        os.makedirs(imgDir, exist_ok=True)

        # Renumber the cameras
        SEDcreator_utils.renumberSEDCameras(context)
        sedCameras = SEDcreator_utils.getSEDCameras()
        # Array of the cameras which render an image
        camerasObjs = sedCameras[renderProp.start:renderProp.end + 1]

        print("---------- Save cameras attributes start ----------")
        cameras_locations, cameras_angle = self.launchCamerasAttributes(context, camerasObjs)
        self.saveCamerasAttributes(context, imgDir, cameras_locations, cameras_angle)
        print("---------- Save cameras attributes end ----------")

        return {'FINISHED'}

    def saveCamerasAttributes(self, context, imgDir, cams_locations, cams_angle):
        # pas sur que ca marche ca
        cameras_attributes_file = os.path.join(imgDir, "cameras_attributes.npz")
        np.savez(cameras_attributes_file, cameras_locations=cams_locations, cameras_angle=cams_angle)

    def launchCamerasAttributes(self, context, camerasObjs):
        # code pas optimal mais pas grave
        cameras_locations, cameras_angle = zip(*[(cam.location, cam.location) for cam in camerasObjs])
        cameras_locations = np.array(cameras_locations)
        cameras_angle = np.array(cameras_angle)
        #for cam in camerasObjs:
        #    cameras_locations = np.append(cam.location)
        #    cameras_angle = np.append(cam.angle)
        return cameras_locations, cameras_angle

class SaveCamerasAttributesProperties(bpy.types.PropertyGroup):
    bool_cameras: bpy.props.BoolProperty(name="Cameras",
                                         description="Write cameras attributes to a txt file",
                                         default=True)

classes = [SaveCamerasAttributesProperties, SaveCamerasAttributesOperator]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.SaveCamerasAttributesProperties = bpy.props.PointerProperty(type=SaveCamerasAttributesProperties)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.SaveCamerasAttributesProperties


if __name__ == "__main__":
    register()
