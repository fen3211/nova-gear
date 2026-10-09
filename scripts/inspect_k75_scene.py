import bpy

print("="*60)
print("INSPECTING SCENE:", bpy.data.filepath)
print("="*60)
print(f"Total objects: {len(bpy.data.objects)}")
for obj in bpy.data.objects[:20]:
    print(f"  - {obj.name} ({obj.type}) at {obj.location}")
if len(bpy.data.objects) > 20:
    print(f"  ... and {len(bpy.data.objects)-20} more objects")

print("\nCAMERAS:")
for cam in bpy.data.cameras:
    print(f"  - {cam.name}")

print("\nLIGHTS:")
for l in bpy.data.lights:
    print(f"  - {l.name} ({l.type}) energy={l.energy}")

print("\nMATERIALS:")
for m in bpy.data.materials[:15]:
    print(f"  - {m.name}")
