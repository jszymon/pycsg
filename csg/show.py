try:
    from OpenGL.GL import glLightfv, GL_LIGHT0, GL_AMBIENT, GL_DIFFUSE
    from OpenGL.GL import GL_POSITION, GL_LIGHTING, GL_DEPTH_TEST, GL_PROJECTION
    from OpenGL.GL import GL_MODELVIEW, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
    from OpenGL.GL import GL_COMPILE, GL_FRONT, GL_SPECULAR, GL_SHININESS
    from OpenGL.GL import GL_POLYGON
    from OpenGL.GL import glEnable, glMatrixMode, glClear, glPushMatrix
    from OpenGL.GL import glTranslatef, glRotatef, glGenLists, glNewList
    from OpenGL.GL import glMaterialfv, glMaterialf, glColor4fv, glBegin
    from OpenGL.GL import glEnd, glNormal3fv, glVertex3fv, glEndList, glCallList
    from OpenGL.GL import glPopMatrix, glFlush
    from OpenGL.GLUT import glutInit, glutSwapBuffers, glutPostRedisplay
    from OpenGL.GLUT import glutInitWindowSize, glutCreateWindow, glutSetOption
    from OpenGL.GLUT import glutInitDisplayMode, GLUT_DEPTH, GLUT_DOUBLE
    from OpenGL.GLUT import GLUT_RGBA, GLUT_ACTION_ON_WINDOW_CLOSE
    from OpenGL.GLUT import GLUT_ACTION_CONTINUE_EXECUTION, GLUT_KEY_LEFT
    from OpenGL.GLUT import GLUT_KEY_RIGHT, GLUT_KEY_DOWN, GLUT_KEY_UP
    from OpenGL.GLUT import glutDisplayFunc, glutKeyboardFunc, glutMainLoop
    from OpenGL.GLUT import glutLeaveMainLoop, glutSpecialFunc
    from OpenGL.GLU import gluPerspective, gluLookAt
    _have_OpenGL = True
except:
    _have_OpenGL = False


from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.pyplot import gcf

from csg.core import CSG
from csg.geom import Vertex, Vector



class TestRenderable:
    light_ambient = [0.3, 0.3, 0.3, 1.0]
    light_diffuse = [0.7, 0.7, 0.7, 1.0]  # Red diffuse light
    light_position = [100.0, 100.0, 100.0, 0.0]  # Infinite light location.

    def __init__(self, csg):
        self.faces = []
        self.normals = []
        self.vertices = []
        self.colors = []
        self.vnormals = []
        self.list = -1
        self.rot_x = 0.0
        self.rot_z = 0.0
        
        polygons = csg.toPolygons()
        
        for polygon in polygons:
            n = polygon.plane.normal
            indices = []
            for v in polygon.vertices:
                pos = [v.pos.x, v.pos.y, v.pos.z]
                if not pos in self.vertices:
                    self.vertices.append(pos)
                    self.vnormals.append([])
                index = self.vertices.index(pos)
                indices.append(index)
                self.vnormals[index].append(v.normal)
            self.faces.append(indices)
            self.normals.append([n.x, n.y, n.z])
            self.colors.append([1.0, 0.0, 0.0, 1.0])
        
        # setup vertex-normals
        ns = []
        for vns in self.vnormals:
            n = Vector(0.0, 0.0, 0.0)
            for vn in vns:
                n = n.plus(vn)
            n = n.dividedBy(len(vns))
            ns.append([a for a in n])
        self.vnormals = ns
        
    def init(self):
        # Enable a single OpenGL light.
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.light_diffuse)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
        glEnable(GL_LIGHT0);
        glEnable(GL_LIGHTING);

        # Use depth buffering for hidden surface elimination.
        glEnable(GL_DEPTH_TEST);

        # Setup the view of the cube.
        glMatrixMode(GL_PROJECTION);
        gluPerspective(40.0, 640./480., 1.0, 10.0);
        glMatrixMode(GL_MODELVIEW);
        gluLookAt(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.)
        
    def render(self):
        if self.list < 0:
            self.list = glGenLists(1)
            glNewList(self.list, GL_COMPILE)
            
            for n, f in enumerate(self.faces):
                glMaterialfv(GL_FRONT, GL_DIFFUSE, self.colors[n])
                glMaterialfv(GL_FRONT, GL_SPECULAR, self.colors[n])
                glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
                glColor4fv(self.colors[n])
            
                glBegin(GL_POLYGON)
                if self.colors[n][0] > 0:
                    glNormal3fv(self.normals[n])

                for i in f:
                    if self.colors[n][1] > 0:
                        glNormal3fv(self.vnormals[i])
                    glVertex3fv(self.vertices[i])
                glEnd()
            glEndList()
        glCallList(self.list)
        
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glTranslatef(0.0, 0.0, -1.0);
        glRotatef(self.rot_x, 1.0, 0.0, 0.0);
        glRotatef(self.rot_z, 0.0, 1.0, 0.0);

        self.render()

        glPopMatrix()
        glFlush()
        glutSwapBuffers()
        #glutPostRedisplay()

    def keypress(self, key, x, y):
        if key == b"q":
            glutLeaveMainLoop()
    def special_keypress(self, key, x, y):
        if key == GLUT_KEY_LEFT:
            self.rot_z += 0.3
        if key == GLUT_KEY_RIGHT:
            self.rot_z -= 0.3
        if key == GLUT_KEY_DOWN:
            self.rot_x -= 0.3
        if key == GLUT_KEY_UP:
            self.rot_x += 0.3
        glutPostRedisplay()

def show_OpenGL(csg):
    if not _have_OpenGL:
        raise RuntimeError("PyOpenGL not available")
    renderable = TestRenderable(csg)
    
    glutInit()
    glutInitWindowSize(640,480)
    renderable.win_id = glutCreateWindow("CSG Test")
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION)
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)
    glutDisplayFunc(renderable.display)
    glutKeyboardFunc(renderable.keypress)
    glutSpecialFunc(renderable.special_keypress)
     
    renderable.init()

    glutMainLoop()

def show_matplotlib(csg):
    verts = []
    polygons = csg.toPolygons()
    for polygon in polygons:
        poly_verts = list()
        for v in polygon.vertices:
            poly_verts.append((v.pos.x, v.pos.y, v.pos.z))
        verts.append(poly_verts)
    ax = gcf().add_subplot(111, projection='3d')
    c = Poly3DCollection(verts)
    c.set_edgecolor("black")
    ax.add_collection3d(c)
    
if __name__ == '__main__':
    a = CSG.cube(radius=[0.5]*3)
    from matplotlib.pyplot import show
    show_matplotlib(a)
    show()
    show_OpenGL(a)
    print("Done")
