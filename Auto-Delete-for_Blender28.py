import bpy
#import rna_keymap_ui
bl_info = {
	"name": "Auto Delete :)",
	"location": "View3D > Add > Mesh > Auto Delete,",
	"description": "Auto detect a delete elements",
	"author": "Vladislav Kindushov",
	"version": (0, 3),
	"blender": (2, 80, 0),
	"category": "Mesh",
}

obj = None
mesh = None
keys = []


def CreateHotkey():
	global keys
	wm = bpy.context.window_manager
	addon_keyconfig = wm.keyconfigs.addon
	kc = addon_keyconfig
	km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
	kmi = km.keymap_items.new(idname='view3d.autodelete', type='X', value='PRESS', alt=False)
	keys.append((km, kmi))

class WM_OT_AutoDelete(bpy.types.Operator):
	""" Dissolves mesh elements based on context instead
	of forcing the user to select from a menu what
	it should dissolve.
	"""
	bl_idname = "view3d.autodelete"
	bl_label = "Auto Delete"
	bl_options = {'UNDO'}


	@classmethod
	def poll(cls, context):
		return context.space_data.type == "VIEW_3D"

	def execute(self, context):
		if bpy.context.mode == 'OBJECT':
			sel = bpy.context.selected_objects

			bpy.ops.object.delete(use_global=True)
		# print ('fdfsd')
		elif bpy.context.mode == 'EDIT_MESH':
			select_mode = context.tool_settings.mesh_select_mode
			me = context.object.data
			if select_mode[0]:
				vertex = me.vertices

				bpy.ops.mesh.dissolve_verts()

				if vertex == me.vertices:
					bpy.ops.mesh.delete(type='VERT')


			elif select_mode[1] and not select_mode[2]:
				edges1 = me.edges

				bpy.ops.mesh.dissolve_edges(use_verts=True, use_face_split=False)
				if edges1 == me.edges:
					bpy.ops.mesh.delete(type='EDGE')



			elif select_mode[2] and not select_mode[1]:
				bpy.ops.mesh.delete(type='FACE')
			else:
				bpy.ops.mesh.dissolve_verts()

		elif bpy.context.mode == 'EDIT_CURVE':
			bpy.ops.curve.delete(type='VERT')
		return {'FINISHED'}



addon_keymaps = []


def get_addon_preferences():
	''' quick wrapper for referencing addon preferences '''
	addon_preferences = bpy.context.user_preferences.addons[__name__].preferences
	return addon_preferences


def get_hotkey_entry_item(km, kmi_value):
	'''
	returns hotkey of specific type, with specific properties.name (keymap is not a dict, so referencing by keys is not enough
	if there are multiple hotkeys!)
	'''
	for i, km_item in enumerate(km.keymap_items):
		if km.keymap_items[i].idname == kmi_value:
			return km_item
	return None



class WM_OT_Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	def draw(self, context):
		layout = self.layout
		# ---------------------------------
		keymap_item = context.window_manager.keyconfigs.addon.keymaps['3D View'].keymap_items
		row = layout.row()
		row.label(text=keymap_item['view3d.autodelete'].name)
		row.prop(keymap_item['view3d.autodelete'], 'type', text='', full_event=True)
		layout.separator()


def register():
	bpy.utils.register_class(WM_OT_AutoDelete)
	CreateHotkey()
	bpy.utils.register_class(WM_OT_Preferences)


def unregister():
	for km, kmi in keys:
		km.keymap_items.remove(kmi)
	bpy.utils.unregister_class(WM_OT_AutoDelete)
	bpy.utils.unregister_class(WM_OT_Preferences)

if __name__ == "__main__":
	register()

