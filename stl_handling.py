'''
Generate a full relationship between F <-> E <-> V
from an STL file (Triangle List).
'''
import struct
import os

def read_stl(addr):
    '''
    Detect the type of STL File
    '''
    try:
        f = open(addr, 'r', encoding='utf-8')
        f.close()
        tria_list = read_stl_ascii(addr)
    except UnicodeDecodeError:
        tria_list = read_stl_bin(addr)

    return tria_list

def read_stl_bin(addr):
    '''
    Parse the Binary encoded STL file and return the list of triangles
        The corresponding list of Normals is skipped as some put it as 0 vec.
        The Number of Triangles are skipped as some put it as 0.
        The header is also skipped.
    List of triangles:[[[T1P1],[T1P2],[T1P3]],
                       [[T2P1],[T2P2],[T2P3]],
                       [[T3P1],[T3P2],[T3P3]],...]
    
    '''
    tria_list = []
    tria_count = 0
    with open(addr, 'rb') as bin_stl:
        # Header 80 bytes, Number of Triangles 4 bytes.
        bin_stl.read(80)
        bin_stl.read(4)

        while True:
            tria_deets = bin_stl.read(50)
            if tria_deets:
                tria_count += 1
                
                # # Normals: Skipped
                # norm_comps = []
                # norm_comps.append(struct.unpack('<f', tria_deets[:4])[0])
                # norm_comps.append(struct.unpack('<f', tria_deets[4:8])[0])
                # norm_comps.append(struct.unpack('<f', tria_deets[8:12])[0])
                # normals.append(norm_comps)

                verts = []
                vertlist = []
                verts.append(struct.unpack('<f', tria_deets[12:16])[0])
                verts.append(struct.unpack('<f', tria_deets[16:20])[0])
                verts.append(struct.unpack('<f', tria_deets[20:24])[0])
                vertlist.append(verts)

                verts = []
                verts.append(struct.unpack('<f', tria_deets[24:28])[0])
                verts.append(struct.unpack('<f', tria_deets[28:32])[0])
                verts.append(struct.unpack('<f', tria_deets[32:36])[0])
                vertlist.append(verts)

                verts = []
                verts.append(struct.unpack('<f', tria_deets[36:40])[0])
                verts.append(struct.unpack('<f', tria_deets[40:44])[0])
                verts.append(struct.unpack('<f', tria_deets[44:48])[0])
                vertlist.append(verts)

                tria_list.append(vertlist)
            else:
                print('The end of STL file. Has', tria_count, 'triangles.')
                break

    return tria_list

def read_stl_ascii(addr):
    '''
    Parse the ASCII encoded STL file and return the list of triangles.
        The corresponding list of Normals is skipped as some put it as 0 vec.
        The Number of Triangles are skipped as some put it as 0.
        The header is also skipped.
    '''
    l = []
    with open(addr, 'r', encoding='utf-8') as f:
        for lines in f:
            l.append(lines)

    list_iter = iter(l)

    tria_list = []
    tria_count = 0

    # Skip header
    next(list_iter)
    while True:
        item = next(list_iter)
        # Check if not end of file - endsolid
        if item[:8] == 'endsolid':
            print('The end of STL file. Has', tria_count, 'triangles.')
            break
        # # Get - facet normal : Skipped Step
        # normal = item.lstrip()[13:-1]
        # components = normal.split(' ')
        # normals.append([float(x) for x in components])
        
        tria_count += 1

        # Skip - outer loop
        next(list_iter)
        # Get - vertex
        verts = []
        vertex = next(list_iter).lstrip()[7:-1]
        vertices = vertex.split(' ')
        verts.append([float(x) for x in vertices])
        # Get - vertex
        vertex = next(list_iter).lstrip()[7:-1]
        vertices = vertex.split(' ')
        verts.append([float(x) for x in vertices])
        # Get - vertex
        vertex = next(list_iter).lstrip()[7:-1]
        vertices = vertex.split(' ')
        verts.append([float(x) for x in vertices])
        tria_list.append(verts)
        # Skip - endloop
        next(list_iter)
        # Skip - endfacet
        next(list_iter)

    return tria_list

def save_stl(file_name, faces):
    '''
    Store the generated file as a new binary STL File.
    '''
    facet_count = len(faces)
    title_str = 'Generated by Vihang\'s STL Converter'
    with open(file_name, 'w',encoding="utf8") as f:
        f.write(title_str)
    empty = b'\x51'
    with open(file_name, 'ab') as bin_stl:
        #header
        # f.write(title_str)
        bin_stl.write(empty * (79-len(title_str)))
        bin_stl.write(b'\x0c')
        #Num Tria
        bin_stl.write(struct.pack('@L', int(facet_count)))
        for i in range(facet_count):
            for comp in range(3):
                bin_stl.write(struct.pack('<f', float(comp)))
            for vertex in faces[i]:
                for coord in vertex:
                    bin_stl.write(struct.pack('<f', float(coord)))
            bin_stl.write(struct.pack('@h', 0))

def list_gen(tria_list):
    '''
    Generate a list of Vertexs, and Indexed sets of Edges and Faces.
    Vertex: Vertex[i] = [x,y,z]
    Edge: Edge[i] = [p1,p2]
    Face: Face[i] = [p1,p2,p3]
    '''
    v_list = []
    e_list = []
    f_list = []

    num_trias = len(tria_list)

    for i in range(num_trias):
        face = []
        for j in tria_list[i]:
            if j not in v_list:
                v_list.append(j)
            face.append(v_list.index(j))
        f_list.append(face)
        
        if [face[0], face[1]] not in e_list and [face[1], face[0]] not in e_list:
            e_list.append([face[0], face[1]])

        if [face[1], face[2]] not in e_list and [face[2], face[1]] not in e_list:
            e_list.append([face[1], face[2]])

        if [face[0], face[2]] not in e_list and [face[2], face[0]] not in e_list:
            e_list.append([face[2], face[0]])

    return v_list, e_list, f_list

def vertex_set(v_list, e_list, f_list):
    '''
    Produce a list of Vertexs and corresponding related elements
    Vertex: Vertex[i] = [[Edge1, Edge2, ...], [Face1, Face2, ...]]
    '''
    num_vertices = len(v_list)

    vertex_detailed = []
    for i in range(num_vertices):
        vertex_detailed.append([[],[],[]])

    for i, edge in enumerate(e_list):
        vertex_detailed[edge[0]][1].append(i)
        vertex_detailed[edge[1]][1].append(i)

    for i, face in enumerate(f_list):
        vertex_detailed[face[0]][2].append(i)
        vertex_detailed[face[1]][2].append(i)
        vertex_detailed[face[2]][2].append(i)

    return vertex_detailed

def edge_set(v_list, e_list, f_list):
    '''
    Produce a list of Vertexs and corresponding Indexed Edge Set
    Edge: Edge[i] = [[Vertex1, Vertex2], [Edge1, Edge2, ...], [FaceL, FaceR]]
    '''
    num_edges = len(e_list)

    edge_detailed = []
    for i, edge in enumerate(e_list):
        edge_detailed.append([[],[],[]])
        edge_detailed[i][0] = edge

    for i, edge in enumerate(e_list):
        edge_detailed[edge[0]][1].append(i)
        edge_detailed[edge[1]][1].append(i)

    for i, face in enumerate(f_list):
        edge_detailed[face[0]][2].append(i)
        edge_detailed[face[1]][2].append(i)
        edge_detailed[face[2]][2].append(i)

    return edge_detailed

def face_set(v_list, e_list, f_list):
    '''
    Produce a list of Vertexs and corresponding Indexeed Face Set
    Face: Face[i] = [[Vertex1, Vertex2, Vertex3], [Edge1, Edge2, Edge3], [Face1, Face2, Face3]]
    '''
    num_vertices = len(v_list)

    vertex_detailed = []
    for i in range(num_vertices):
        vertex_detailed.append([[],[],[]])

    for i, edge in enumerate(e_list):
        vertex_detailed[edge[0]][1].append(i)
        vertex_detailed[edge[1]][1].append(i)

    for i, face in enumerate(f_list):
        vertex_detailed[face[0]][2].append(i)
        vertex_detailed[face[1]][2].append(i)
        vertex_detailed[face[2]][2].append(i)

    return vertex_detailed

def get_sets(v_list, e_list, f_list):
    '''
    Get all three sets: Vetrex, Edge and Face Sets in that order.
    '''
    return vertex_set(v_list, e_list, f_list), edge_set(v_list, e_list, f_list), face_set(v_list, e_list, f_list)

def higher_res():
    '''
    Increase the resolution of the Model by 1/sqrt(3) side method.
    Computes Voronoi Dual and combines the 2 meshes.
    '''
    return None

def main():
    os.chdir('D:\\Codes\\Geometric\\')

    # path = input('Enter the path to STL: ')
    triangles = read_stl('Octahedron.stl')

    vertices, edges, faces = list_gen(tria_list=triangles)

    print('Number of verts:', len(vertices))
    print('Number of edges:', len(edges))
    print('Number of faces:', len(faces))

    print('For Point #2 in the STL,')
    print('\tCo-ordinates:', vertices[1])
    print('\tShared Edges:', edges)
    print('\tShared Faces:', faces)

    vertices_complete = vertex_set(vertices, edges, faces)
    edges_complete = edge_set(vertices, edges, faces)
    faces_complete = face_set(vertices, edges, faces)

    for i,deets in enumerate(vertices_complete):
        print('Vertex #', i)
        print(deets)

if __name__ == '__main__':
    main()
