import MDAnalysis as mda
import numpy as np
import pandas as pd
import math

def label_np(core, nptype = 'Janus'):
    """
    Depending on the type of NP we want in the input, we can try to generate 
    different patterns on the surface of the spehre, which will help us generate the 
    lists correponding to the anisotropic nature of the NP. 
        
    The types of NPs we can currently have are:
        
    - Janus 
    - Striped
    
    More options will be added. As in its current iteraton:
    
    1. The Janus type divides the NP into two hemispheres.
    
    2. The Striped type divides the NP into three hemispheres, typically used with a hydrophobic middle 
    especially when it comes to using with biosimulations. 
        
    Args:
    Core: 
    Placeholder
        Type:
    Placeholder
    Returns:
        
    Raises:
    
    """
    xcoordinates = [i[0] for i in core] # Find x coordinates
    ycoordinates = [i[1] for i in core] # Find y coordinates
    zcoordinates = [i[2] for i in core] # Find z coordinates 
    length = 2 * abs(max(zcoordinates)) # From 2 * the radius, we know the total length of the NP 
    
    if nptype == 'Striped': 
        # As we have a spherical structure, we just need to find the minimum/maximum in 
        # one of the axes to find that for the rest 
        # define the threshold for how you wish to generate the NP with striped pattern 
        threshold = length / 3 
        # Find the central band of the sphere where you wish to put 
        # different ligands 
        stripedvalues = [i for i in core if i[2] > (min(zcoordinates) + threshold)
                         and i[2] < (max(zcoordinates) - threshold)]
            
        ceilingvalues = [i for i in core if i not in stripedvalues] 
        return [stripedvalues, ceilingvalues]
            
    elif nptype == 'Janus':
        # Same logic as with the striped example, but with the Janus pattern 
        threshold = length / 2 
        topvalues = [i for i in core if i[2] > (min(zcoordinates) + threshold)] 
        botvalues = [i for i in core if i not in topvalues] # Return bottom hemisphere 
        return [topvalues, botvalues]

def fibanocci_sphere(samplepoints):
    """ Return a Fibanocci sphere with N number of points on the surface. 
        This will act as the template for the nanoparticle core. 
    """
    points = []
    phi = math.pi * (3. - math.sqrt(5.))  # golden angle in radians
    
    for i in range(samplepoints):
        y = 1 - (i / float(samplepoints - 1)) * 2  # y goes from 1 to -1
        radius = math.sqrt(1 - y * y)  # radius at y
        
        theta = phi * i  # golden angle increment
        x = math.cos(theta) * radius
        z = math.sin(theta) * radius
        points.append((x, y, z))    
    return points

    
def generate_core(radius, n, option = 'Plain'):
    """ Creates a Fibanocci sphere that represents the NP core 
        and allocates the radius. 

        The core is scaled down/up to the size that one wishes to have. 
        We can generate arrays corresponding  to a plain core, or a tuple with 
        two entries with different parts of the NP core that corresponds to positions 
        with striped or janus type positions.
    """
    spherelist = [] 
    sphere = fibanocci_sphere(n) # Create the fibanocci sphere representing the NP core 
    xsphere, ysphere, zsphere  = [], [], []

    for entry in sphere:
        xsphere.append(entry[0])
        ysphere.append(entry[1])
        zsphere.append(entry[2])
        
    # Append as 2d list
    for index in range(0, len(xsphere)):
        spherelist.append([xsphere[index], ysphere[index], zsphere[index]])
    # Take the radius value, and then multiply the unit vector in each 
    # Direction by that radius value to increase the total volume of the 
    # NP core.
    for index in range(0, len(spherelist)-1):
        spherelist[index][0] = spherelist[index][0] * radius
        spherelist[index][1] = spherelist[index][1] * radius
        spherelist[index][2] = spherelist[index][2] * radius
    # Return just the whole list without any further modifications
    if option == 'Plain':
        return [spherelist[1:-1]]
    # Separate out the anisotropy for the Striped variant 
    elif option == 'Striped':
        stripedvalues, ceilingvalues = label_np(spherelist[1:-1], option)[0], label_np(spherelist[1:-1], option)[1]
        return stripedvalues, ceilingvalues
    # Separate out the anisotropy for the Janus variant 
    elif option == 'Janus':
        topvalues, bottomvalues = label_np(spherelist[1:-1], option)[0], label_np(spherelist[1:-1], option)[1]  
        return topvalues, bottomvalues

def rotation_matrix_from_vectors(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2
    Args:
        vec1: 
            A 3d "source" vector
        vec2: 
            A 3d "destination" vector
    Returns:
        rotation_matrix:
            A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    Raises:
    """
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

def pandas_np(ligandstring, firstatom, lastatom, spherelist, 
                   ligandname, corename, length = 1.0):
    """Placeholder
    """
    transformationlist, namelist = [], [] 
    ligandlist = [] 
    sphere = []
    xplot, yplot, zplot = [], [], []
    xplotsphere, yplotsphere, zplotsphere = [], [], []
    u = mda.Universe.from_smiles(LigandString)
    ligand = u.select_atoms('all')
    logging.info(f"The length of the ligand is {len(Ligand)}")
    firstatomgroup = u.select_atoms('name {}'.format(firstatom))
    lastatomgroup = u.select_atoms('name {}'.format(lastatom))
    ligandalignmentvector = (firstatomgroup.positions- lastatomgroup.positions)[0]
    
    for i,j in enumerate(ligand.positions):
        vector = (j - firstatomgroup.positions)[0]
        vector[0] = ligandalignmentvector[0] - vector[0]
        vector[1] = ligandalignmentvector[1] - vector[1]    
        vector[2] = ligandalignmentvector[2] - vector[2]
        if vector[0] == -math.inf:
            pass
        if vector[0] == 0.0:
            pass
        else:
            transformationList.append([vector, Ligand.atoms[i].type])        
        
    unitvector = np.linalg.norm(ligandalignmentvector)
    vecligand = ligandalignmentvector.tolist()

    # Loop over the sphere and find the 
    for index in range(0, len(spherelist)):
        vec2 = spherelist[index]
        # Find the transformationvector for the ligand vector to vec2, which is the position of the point on sphere
        transformationvector = rotation_matrix_from_vectors(vecligand, vec2)
        # Rotate the vector 
        vec1rot = transformationvector.dot(vecligand) # Rotate the vector to match the surface point on the sphere 
        # Get the absolute length of the unit vector 
        unitvectorabs = np.linalg.norm(ligandalignmentvector)
        # Change the rotation vector in unit vector, then multiply by the absolute 
        # length of the sphere 
        vecmultiplier = vec1rot/unitvectorabs * (np.linalg.norm(np.array(vec2))) + (vec1rot/unitvectorabs * length)
        # Find the difference in length 
        sphere.append(vec2)
        # Translate the vector further out 
        for trans in transformationlist:
            ligandatomcoordinate = transformationvector.dot(trans[0])
            ligandatomcoordinate[0] = ligandatomcoordinate[0] + vecmultiplier[0]
            ligandatomcoordinate[1] = ligandatomcoordinate[1] + vecmultiplier[1]
            ligandatomcoordinate[2] = ligandatomcoordinate[2] + vecmultiplier[2]
            ligandlist.append(ligandatomcoordinate.tolist()) # Append coordinates of the 
            namelist.append(trans[1]) # Append the names of the atoms
    # Append the coordinates of the ligands 
    for index, entry in enumerate(ligandlist):
        xplot.append(entry[0])
        yplot.append(entry[1])
        zplot.append(entry[2])  
    
    ligandconstituent = [atom.name for atom in ligand]
    ligands = []
    for index in range(0, len(sphere)): 
        ligands = ligands + ligandconstituent

    spherename = [] 
    # Append the coordinates of the sphere 
    for entry in sphere:
        xplotsphere.append(entry[0])
        yplotsphere.append(entry[1])
        zplotsphere.append(entry[2])
        spherename.append('P5')
    
    dfligand = pd.DataFrame(list(zip(xplot, yplot, zplot, ligands)),
                            columns =['X', 'Y', 'Z', 'NAME'])
    
    dfcore = pd.DataFrame(list(zip(xplotsphere, yplotsphere, zplotsphere, spherename)),
                          columns =['X', 'Y', 'Z', 'NAME'])
        
    dfligand['RESNAME'] = ligandname
    dfcore['RESNAME'] = corename
    return dfligand, dfcore
 

def pandas_np_martini(molecule, ligandalignmentvector, transformationlist, spherelist, ligandname, 
                      corename, length = 1.0):
    """ Function to read Martini molecule information and orientate on NP surface"""
    
    ligandlist, namelist = [], []
    sphere = []
    xplot, yplot, zplot = [], [], []
    xplotsphere, yplotsphere, zplotsphere = [], [], []

    # Sulfur/ligand vector 

    unitVector = np.linalg.norm(ligandalignmentvector)
    vec1 = ligandalignmentvector.tolist()

    for index in range(0, len(spherelist)):
        vec2 = spherelist[index] 
        transformationvector = rotation_matrix_from_vectors(vec1, vec2)  
        vec1rot = transformationvector.dot(vec1) # Rotate the vector to match the surface point on the sphere 
        unitvectorabs = np.linalg.norm(ligandalignmentvector)  
        vecmultiplier = vec1rot/unitvectorabs * (np.linalg.norm(np.array(vec2))) + (vec1rot/unitvectorabs * length)
        sphere.append(vec2)
        
        # Get the factors to translate the vector 
        for trans in transformationlist:
                
            ligandatomcoordinate = transformationvector.dot(trans[0])
            ligandatomcoordinate[0] = ligandatomcoordinate[0] + vecmultiplier[0]
            ligandatomcoordinate[1] = ligandatomcoordinate[1] + vecmultiplier[1]
            ligandatomcoordinate[2] = ligandatomcoordinate[2] + vecmultiplier[2]
            ligandlist.append(ligandatomcoordinate.tolist()) 
            namelist.append(trans[1]) # Append the names of the atoms 

    # Append the coordinates of the ligands 
    for index, entry in enumerate(ligandlist):
        xplot.append(entry[0])
        yplot.append(entry[1])
        zplot.append(entry[2])
        
    # Add in the ligand index 
    ligandconstituent = [atom.name for atom in molecule] # Molecule is utilized here 
    ligands = []
    for index in range(0, len(sphere)): 
        ligands = ligands + ligandconstituent
    
    spherename = [] 
    # Append the coordinates of the sphere 
    for entry in sphere:
        xplotsphere.append(entry[0])
        yplotsphere.append(entry[1])
        zplotsphere.append(entry[2])
        spherename.append('P5')
            
    dfligand = pd.DataFrame(list(zip(xplot, yplot, zplot, ligands)),
                            columns =['X', 'Y', 'Z', 'NAME'])

    dfligand['RESNAME'] = ligandname
            
    dfcore = pd.DataFrame(list(zip(xplotsphere, yplotsphere, zplotsphere, spherename)),
                          columns =['X', 'Y', 'Z', 'NAME'])

    dfcore['RESNAME'] = corename
    return dfligand, dfcore

def read_martini_molecules(grofile, first, last):
    """ Generate the normalized coordinates, name, and vector of the Martini molecule 
    
    Access the Martini3 small molecules library and reads the parameterized coordinates from it, 
    with future view of looking at generating automatically generating Martini 3 representations 
    from smiles strings 
    
    One needs to describe the attaching bead to the main core and the atom furthest away from the 
    core, to create the directional vector to which the struture will be placed on the surface of the NP 
    core. 
    
    Args:
        GroFile:
          path the gromacs file of the ligand
    Returns: 
        Placeholder
    Raises: 
        Placeholder 
        
    """
    transformationlist = []
    martiniuniverse = mda.Universe(grofile) # Load the Martini gro file in as a universe 
    ids = [i.name for i in martiniuniverse.atoms]
    molecule = martiniuniverse.select_atoms('all')
    # In this case, the atoms will be N1 and R3 
    firstatom = molecule.select_atoms('name {}'.format(first)) 
    lastatom = molecule.select_atoms('name {}'.format(last))
    ligandalignmentvector = (firstatom.positions - lastatom.positions)[0] # Get the alignment vector created from the first and COM  
    
    # Loop over the positions 
    for i,j in enumerate(molecule.positions):
        vector = (j - firstatom.positions)[0]
        vector[0] = ligandalignmentvector[0] - vector[0]
        vector[1] = ligandalignmentvector[1] - vector[1]    
        vector[2] = ligandalignmentvector[2] - vector[2]
        
        if vector[0] == -math.inf:
            pass
        if vector[0] == 0.0:
            pass
        else:
            transformationlist.append([vector, molecule.atoms[i].type])   
            
    # Return the universe, the transformed (normalized) coordinate list of the ligand molecule, and the 
    # alignment vector that shows the arrow of direction of the vector, which we will be able to reorientate
    return molecule, transformationlist, ligandalignmentvector 
