import bpy
import rna_keymap_ui
bl_info = {
	"name": "Auto Delete :)",
	"location": "View3D > Add > Mesh > Auto Delete,",
	"description": "Auto detect a delete elements",
	"author": "Vladislav Kindushov",
	"version": (0, 2),
	"blender": (2, 80, 0),
	"category": "Mesh",
}

obj = None
mesh = None


def find_connected_verts(me, found_index):
	edges = me.edges
	connecting_edges = [i for i in edges if found_index in i.vertices[:]]
	# print('connecting_edges',len(connecting_edges))
	return len(connecting_edges)


class AutoDelete(bpy.types.Operator):
	""" Dissolves mesh elements based on context instead
	of forcing the user to select from a menu what
	it should dissolve.
	"""
	bl_idname = "view3d.autodelete"
	bl_label = "Auto Delete"
	bl_options = {'UNDO'}

	use_verts = bpy.props.BoolProperty(name="Use Verts", default=False)

	@classmethod
	def poll(cls, context):
		return context.space_data.type == "VIEW_3D"

	# return (context.active_object is not None)# and (context.mode == "EDIT_MESH")

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

				bpy.ops.mesh.select_mode(type='EDGE')

				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.mode_set(mode='EDIT')
				vs = [v.index for v in me.vertices if v.select]
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')

				for v in vs:
					vv = find_connected_verts(me, v)
					if vv == 2:
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


# bpy.utils.register_class(MeshDissolveContextual_OT_vlad)


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


def add_hotkey():
	user_preferences = bpy.context.preferences
	addon_prefs = user_preferences.addons[__name__].preferences

	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon
	km = kc.keymaps.new(name="3D View Generic", space_type='VIEW_3D', region_type='WINDOW')
	kmi = km.keymap_items.new(AutoDelete.bl_idname, 'X', 'PRESS', shift=False, ctrl=False, alt=False)
	# kmi.properties.name = "view3d.advancedmove"
	kmi.active = True
	addon_keymaps.append((km, kmi))


class AutoDelete_Add_Hotkey(bpy.types.Operator):
	''' Add hotkey entry '''
	bl_idname = "auto_delete.add_hotkey"
	bl_label = "Auto Delete Add Hotkey"
	bl_options = {'REGISTER', 'INTERNAL'}

	def execute(self, context):
		add_hotkey()

		self.report({'INFO'}, "Hotkey added in User Preferences -> Input -> Screen -> Screen (Global)")
		return {'FINISHED'}


def remove_hotkey():
	''' clears all addon level keymap hotkeys stored in addon_keymaps '''
	wm = bpy.context.window_manager
	kc = wm.keyconfigs.user
	km = kc.keymaps['3D View Generic']

	for i in bpy.context.window_manager.keyconfigs.addon.keymaps['3D View Generic'].keymap_items:
		if i.name == 'Auto Delete' or i.name == 'VIEW3D_OT_auto_delete':
			bpy.context.window_manager.keyconfigs.addon.keymaps['3D View Generic'].keymap_items.remove(i)


class StreamExtrudePref(bpy.types.AddonPreferences):
	bl_idname = __name__

	def draw(self, context):
		layout = self.layout
		# ---------------------------------
		box = layout.box()
		split = box.split()
		col = split.column()
		# col.label("Setup Advanced Move")
		col.separator()
		wm = bpy.context.window_manager
		kc = wm.keyconfigs.user
		km = kc.keymaps['3D View Generic']
		kmi = get_hotkey_entry_item(km, "view3d.autodelete")
		if kmi:
			col.context_pointer_set("keymap", km)
			rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
		else:
			col.label("No hotkey entry found")
			col.operator(AutoDelete_Add_Hotkey.bl_idname, text="Add hotkey entry", icon='ZOOMIN')

classes = (AutoDelete, AutoDelete_Add_Hotkey, StreamExtrudePref)

def CreateHotkey():
	global keys
	wm = bpy.context.window_manager
	addon_keyconfig = wm.keyconfigs.addon
	kc = addon_keyconfig
	km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
	kmi = km.keymap_items.new(idname='view3d.advancedmove', type='K', value='PRESS', alt=True)
	keys.append((km, kmi))
	
def register():
	for c in classes:
		bpy.utils.register_class(c)
	CreateHotkey()


def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)
	for km, kmi in keys:
		km.keymap_items.remove(kmi)
if __name__ == "__main__":
	register()

