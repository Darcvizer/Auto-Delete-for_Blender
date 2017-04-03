import bpy
bl_info = {
"name": "Auto Delete :)",
"location": "View3D > Add > Mesh > Auto Delete,",
"description": "Auto detect a delete elements",
"author": "Vladislav Kindushov",
"version": (0,1),
"blender": (2, 7, 7),
"category": "Mesh",
}



 
 
def find_connected_verts(me, found_index):  
    edges = me.edges  
    connecting_edges = [i for i in edges if found_index in i.vertices[:]]  
    #print('connecting_edges',len(connecting_edges))
    return len(connecting_edges)  
 
 
 
class MeshDissolveContextual(bpy.types.Operator):
    """ Dissolves mesh elements based on context instead
    of forcing the user to select from a menu what
    it should dissolve.
    """
    bl_idname = "mesh.dissolve_contextual"
    bl_label = "Mesh Dissolve Contextual"
    bl_options = {'UNDO'}
   
    use_verts = bpy.props.BoolProperty(name="Use Verts", default=False)
 
    @classmethod
    def poll(cls, context):
        return bpy.ops.context.active_objectv
        #return (context.active_object is not None)# and (context.mode == "EDIT_MESH")
   
    def execute(self, context):
        if bpy.context.mode == 'OBJECT':
            sel = bpy.context.selected_objects

            bpy.ops.object.delete()
            #print ('fdfsd')
        elif bpy.context.mode == 'EDIT_MESH':
            select_mode = context.tool_settings.mesh_select_mode
            me = context.object.data
            if select_mode[0]:
                bpy.ops.mesh.dissolve_verts()
            elif select_mode[1] and not select_mode[2]:
                edges1 = me.edges

                bpy.ops.mesh.dissolve_edges(use_verts=True, use_face_split=False)
                if edges1 == me.edges:
                    bpy.ops.mesh.delete(type='EDGE')

                bpy.ops.mesh.select_mode(type='EDGE')
                
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')
                vs = [v.index for v in me.vertices if v.select]
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
               
                for v in vs:
                    vv = find_connected_verts(me, v)
                    if vv==2:
                        me.vertices[v].select = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.dissolve_verts()
                bpy.ops.mesh.select_all(action='DESELECT')
               
                for v in vs:
                    me.vertices[v].select = True

                   
            elif select_mode[2] and not select_mode[1]:
                bpy.ops.mesh.delete(type='FACE')
            else:
                bpy.ops.mesh.dissolve_verts()
           
        elif bpy.context.mode == 'EDIT_CURVE':
            print("ere")
            bpy.ops.curve.delete(type='VERT')
        return {'FINISHED'}
 
bpy.utils.register_class(MeshDissolveContextual)

 

def register():
    #bpy.utils.register_class(SmartDelete)

    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new('mesh.dissolve_contextual', 'X', 'PRESS',)



def unregister():
    bpy.utils.unregister_class(MeshDissolveContextual)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps["3D View"]
        for kmi in km.keymap_items:
            if kmi.idname == 'mesh.dissolve_contextual':
                km.keymap_items.remove(kmi)
                break


if __name__ == "__main__":
    register()