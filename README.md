# SED Creator
***
SEDCreator is a Blender add-on which permits to create cluster of cameras in a scene.

## Installation

+ Compress the _SEDCreator_  folder in a _.zip_ format.
+ Open Blender and go to _Edit_ and then _Preferences_ (or _Ctrl ,_ shortcut).
+ Go to _Add-ons_, _Install_ and choose the _SEDCreator.zip_ previously created.
+ Type _SEDcreator_ in the research bar and you should see _Generic: SEDcreator_. Check the box.
+ Click on the hamburger menu and click on _Save preferences_. You can close this window.

## How to use

- On the _Sidebar_ of the _View menu_ (or press _n_) you have now a _SEDcreator_ tab.

### Scene Management
You can now try to put some cluster in the scene, for that you can  
- Place at least one _Empty_ in the scene and select it (or them) and then click on _Set Project Setup_.  
**Note** : All the setup that you do are effective on the _Empty_ which are selected, if they are not it will not apply anything on them. 
- There are several types of clusters with various options on them (radius, focal length of cameras, orientation of cameras), you can try to know what fit better for your project !  

### Delimitations
The _Delimitations_ are for the _Adaptative Icosahedron_ and _Adaptative UV Sphere_ (only). This is to limit the area of the cameras (i.e. if you place an _Empty_ and some cameras of the cluster are outside the _Delimitations_, they are not created.

### Setup cameras
Click on that button to create or modify the selected _Empty_.

### Render Management
To render, you have to :

    - Check the boxes you want to render (_Albedo_, _Depth_, etc).

    **Note** : Beauty is rendered by default.

    - name the directory you want your renders to be.

    **Note** : The directory will be created next to your Blender file.

    - _First frame_ and _Last frame_ are the range of cameras you want to render. One camera is equal to one frame (with the corresponding numbers). Let say you want to render only _Camera_11_ to _Camera_32_ you put _First frame = 11_ and _Last frame = 32_.
    
    - Click on _Start Render_.

## Two versions
There is two versions of this add-on, one on branch _main_ and another on branch _alternative_version_. What changes is the behaviour during rendering. In the first one, if you hide cameras in the viewport they are rendered as if they where in the scene (and they are numbered as if they were there too). Meanwhile in the second version the hidden cameras does not exist for the renderer (they are not numbered and they are never rendered if they are hidden). 
