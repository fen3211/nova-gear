import bpy
import bmesh
import math

def test_stadium_collar():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh = bpy.data.meshes.new("USBC_Sleeve")
    bm = bmesh.new()
    
    r_out = 0.044
    r_in = 0.036
    dx = 0.14
    n_semi = 16
    depth = 0.10
    
    # Generate points along stadium curve
    def get_stadium_pts(r, dx, n):
        pts = []
        # Right arc: from -pi/2 to pi/2 (exclusive of endpoints to avoid dups)
        for i in range(n + 1):
            th = -math.pi/2.0 + math.pi * i / float(n)
            pts.append((dx/2.0 + r * math.cos(th), r * math.sin(th)))
        # Left arc: from pi/2 to 3pi/2
        for i in range(1, n): # skip 0 and n to avoid dup of top and bottom
            th = math.pi/2.0 + math.pi * i / float(n)
            pts.append((-dx/2.0 + r * math.cos(th), r * math.sin(th)))
        return pts

    pts_out = get_stadium_pts(r_out, dx, n_semi)
    pts_in = get_stadium_pts(r_in, dx, n_semi)
    N = len(pts_out)
    
    # Front rim (y = 0)
    v_front_out = [bm.verts.new((x, 0.0, z)) for x, z in pts_out]
    v_front_in  = [bm.verts.new((x, 0.0, z)) for x, z in pts_in]
    
    # Back rim (y = depth)
    v_back_out  = [bm.verts.new((x, depth, z)) for x, z in pts_out]
    v_back_in   = [bm.verts.new((x, depth, z)) for x, z in pts_in]
    
    bm.verts.ensure_lookup_table()
    
    # Build faces:
    for i in range(N):
        i_next = (i + 1) % N
        # Front lip face (quad)
        bm.faces.new((v_front_out[i], v_front_out[i_next], v_front_in[i_next], v_front_in[i]))
        # Outer cylinder wall (quad)
        bm.faces.new((v_front_out[i], v_back_out[i], v_back_out[i_next], v_front_out[i_next]))
        # Inner cylinder wall (quad - reversed winding for normal pointing inward)
        bm.faces.new((v_front_in[i], v_front_in[i_next], v_back_in[i_next], v_back_in[i]))
        # Back lip face (quad)
        bm.faces.new((v_back_out[i_next], v_back_out[i], v_back_in[i], v_back_in[i_next]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("USBC_Sleeve", mesh)
    bpy.context.scene.collection.objects.link(obj)
    print(f"Collar created successfully! Vertices: {len(mesh.vertices)}, Polygons: {len(mesh.polygons)}")
    return obj

if __name__ == "__main__":
    test_stadium_collar()
