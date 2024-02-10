#import sys
import os
#import re
import bpy
#from glob import glob
from SEDcreator import SEDcreator_prepareRender

def renderCurvature(context, imgDir, imgName):

    # Set up rendering
    scene = context.scene
    render = context.scene.render
    renderProp = context.scene.RenderProperties

    SEDcreator_prepareRender.enableUsePasses(context)

    nodes = context.scene.node_tree.nodes
    links = context.scene.node_tree.links

    # Clear default nodes
    for n in nodes:
        nodes.remove(n)

    # Create input render layer node
    render_layers = nodes.new('CompositorNodeRLayers')

    format = "OPEN_EXR"
    color_depth = "16"

    os.chdir("//")

    SEDcreator_prepareRender.prepareRenderCurvature(renderProp.bool_curvature, context, imgDir, imgName)

    bpy.ops.render.render(write_still=True)  # render still
    return
