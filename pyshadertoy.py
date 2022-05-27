#!/usr/bin/env python3

# see http://www.iquilezles.org/apps/shadertoy/

import sys
import array
import random
import time
import struct

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    print("Cannot find PyOpenGL module")
    sys.exit()

try:
    from OpenGL.GL.ARB.shader_objects import *
    from OpenGL.GL.ARB.fragment_shader import *
    from OpenGL.GL.ARB.vertex_shader import *
except:
    print("Shaders are not supported (need opengl 2.0+)")
    sys.exit()

#import sys
#glutInit(sys.argv)

start_time = 0

width = 512
height = 512

txw = width
txh = height

size = txw * txh
texture = 0
shader_body = ''
fullscreen = 0

buf = (GLuint * size)(0)

def dump():
    a = (GLuint * size)(0)
    glReadPixels(0, 0, txw, txh, GL_RGBA, GL_UNSIGNED_BYTE, a);
    for i in range(txw):
        v = a[i]
#       print "%08x" % (v),
#   print 


def mouse(button, state, x, y):
    motion(x, y)

def motion(x, y):

    flx = x
    fly = height-y

    for iMouse in ('iMouse','mouse'):
        if iMouse in shader_body:
            glUniform4fvARB(Sp.indexOfUniformVariable(iMouse), 1, struct.pack("ffff", flx,fly,0,0))

def gen(param):
    if (param):
        for i in range( size ):
             buf[i] = random.randint(0, 0xffffffff)
    else:
        return
        buf.pop(0)
        buf.append( random.randint(0,0xffffffff) )
    data = array.array("I", buf).tobytes()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, txw, txh, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

def togglefullscreen():
    global fullscreen

    if fullscreen:
        sw, sh = glutGet(GLUT_SCREEN_WIDTH), glutGet(GLUT_SCREEN_HEIGHT)
        glutPositionWindow((sw - width) // 2, (sh - height) // 2)
        glutReshapeWindow(width, height);
    else:
        glutFullScreen()

    glutPostRedisplay()
    fullscreen = not fullscreen

def keyboard(key,x,y):
    key = key.decode()

    if key==chr(27) or key==chr(3):
        os._exit(0)
    elif key=='f':
        togglefullscreen()

    dump()
    gen(0)
    glutPostRedisplay( )

    return 0

def reshape(w, h):
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0, 1, 1, 0, -1, 1);
    glMatrixMode(GL_MODELVIEW);

    for iResolution in ('iResolution', 'resolution'):
        if iResolution in shader_body:
            glUniform2fvARB(Sp.indexOfUniformVariable(iResolution), 1, struct.pack("ff", w, h))


def animation():

    dump()
    gen(0)

    time.sleep(0.01)

    ftime = time.time() - start_time

    for iTime in ('iTime', 'time'):
        if iTime in shader_body:
            glUniform1fvARB(Sp.indexOfUniformVariable(iTime), 1, struct.pack("f", ftime))

    glutPostRedisplay()

def init():

    global buf
    global texture

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)

    for i in range( size ):
         buf[i] = random.randint(0, 0xffffffff)

    gen(1)

    glEnableClientState( GL_TEXTURE_COORD_ARRAY )
    glEnableClientState( GL_VERTEX_ARRAY )
    vertices = array.array('h', [0,0, 1,0, 0,1, 1,1])
    texcoord = array.array('f', [0,0, 1,0, 0,1, 1,1])
    glVertexPointer(2,GL_SHORT, 0, vertices.tobytes())
    glTexCoordPointer(2,GL_FLOAT, 0, texcoord.tobytes())

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glEnable(GL_TEXTURE_2D);


def display( ):
#   glEnable(GL_SCISSOR_TEST);
#   glScissor( 0,0,txw, txh);
    glDisable(GL_DEPTH_TEST);
    glClearColor ( 0.0, 0.0, 0.0, 0.0 )
    glClear(GL_COLOR_BUFFER_BIT)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    glutSwapBuffers()

class ShaderProgram ( object ):
    """Manage GLSL programs."""
    def __init__( self ):
        self.__requiredExtensions = ["GL_ARB_fragment_shader",
            "GL_ARB_vertex_shader",
            "GL_ARB_shader_objects",
            "GL_ARB_shading_language_100",
            "GL_ARB_vertex_shader",
            "GL_ARB_fragment_shader"]
        self.checkExtensions( self.__requiredExtensions )
        self.__shaderProgramID = glCreateProgramObjectARB()
        self.__checkOpenGLError()
        self.__programReady = False
        self.__isEnabled = False
        self.__shaderObjectList = []

    def checkExtensions( self, extensions ):
        """Check if all extensions in a list are present."""
        for ext in extensions:
            if ( not ext ):
                print("Driver does not support ", ext)
                sys.exit()

    def __checkOpenGLError( self ):
        """Print OpenGL error message."""
        err = glGetError()
        if ( err != GL_NO_ERROR ):
            print('GLERROR: ', gluErrorString( err ))
            sys.exit()

    def reset( self ):
        """Disable and remove all shader programs"""
        for shaderID in self.__shaderObjectList:
            glDetachObjectARB( self.__shaderProgramID, shaderID )
            glDeleteObjectARB( shaderID )
            self.__shaderObjectList.remove( shaderID )
            self.__checkOpenGLError( )
        glDeleteObjectARB( self.__shaderProgramID )
        self.__checkOpenGLError( )
        self.__shaderProgramID = glCreateProgramObjectARB()
        self.__checkOpenGLError( )
        self.__programReady = False

    '''
    def addShader( self, shaderType, fileName ):
        """Read a shader program from a file.

        The program is load and compiled"""
        shaderHandle = glCreateShaderObjectARB( shaderType )
        self.__checkOpenGLError( )
        header = """#version 300 es
precision mediump float;
uniform vec2 iResolution;
uniform float iTime;
uniform vec4 iMouse;
"""
        footer = """
out vec4 fragColor;
void main() {
    mainImage(fragColor, gl_FragCoord.xy);
}
"""
        global shader_body
        shader_body = open(fileName, 'r').read()

        sourceString = header + shader_body + footer
        glShaderSourceARB(shaderHandle, [sourceString] )
        self.__checkOpenGLError( )
        glCompileShaderARB( shaderHandle )
        success = glGetObjectParameterivARB( shaderHandle, 
            GL_OBJECT_COMPILE_STATUS_ARB)
        if (not success):
            print(glGetInfoLogARB( shaderHandle ))
            sys.exit( )
        glAttachObjectARB( self.__shaderProgramID, shaderHandle )
        self.__checkOpenGLError( )
        self.__shaderObjectList.append( shaderHandle )

    def linkShaders( self ):
        """Link compiled shader programs."""
        glLinkProgramARB( self.__shaderProgramID )
        self.__checkOpenGLError( )
        success = glGetObjectParameterivARB( self.__shaderProgramID, 
            GL_OBJECT_LINK_STATUS_ARB )
        if (not success):
            print(glGetInfoLogARB(self.__shaderProgramID))
            sys.exit()
        else:
            self.__programReady = True
    '''

    def addShader( self, shaderType, fileName ):
        shaderHandle = glCreateShaderObjectARB( shaderType )
        self.__checkOpenGLError( )

        global shader_body
        shader_body = open(fileName, 'r').read()

        header = "#version 300 es\nprecision mediump float;\nuniform vec2 iResolution;\nuniform float iTime;\nuniform vec4 iMouse;\n"
        footer = "out vec4 fragColor;\nvoid main() { mainImage(fragColor, gl_FragCoord.xy);}\n"

        if 'iResolution' in shader_body:
            shader_body = header + shader_body

        if 'void main(' not in shader_body:
            shader_body += footer

        sourceString = shader_body

        glShaderSourceARB(shaderHandle, [sourceString] )
        self.__checkOpenGLError( )
        glCompileShaderARB( shaderHandle )
        success = glGetObjectParameterivARB( shaderHandle, 
            GL_OBJECT_COMPILE_STATUS_ARB)
        if (not success):
            print(glGetInfoLogARB( shaderHandle ))
            sys.exit( )
        glAttachObjectARB( self.__shaderProgramID, shaderHandle )
        self.__checkOpenGLError( )
        self.__shaderObjectList.append( shaderHandle )

    def linkShaders( self ):
        glLinkProgramARB( self.__shaderProgramID )
        self.__checkOpenGLError( )
        success = glGetObjectParameterivARB( self.__shaderProgramID, 
            GL_OBJECT_LINK_STATUS_ARB )
        if (not success):
            print(glGetInfoLogARB(self.__shaderProgramID))
            sys.exit()
        else:
            self.__programReady = True


    def enable( self ):
        """Activate shader programs."""
        if self.__programReady:
            glUseProgramObjectARB( self.__shaderProgramID )
            self.__isEnabled=True
            self.__checkOpenGLError( )
        else:
            print("Shaders not compiled/linked properly, enable() failed")

    def disable( self ):
        """De-activate shader programs."""
        glUseProgramObjectARB( 0 )
        self.__isEnabled=False
        self.__checkOpenGLError( )

    def indexOfUniformVariable( self, variableName ):
        """Find the index of a uniform variable."""
        if not self.__programReady:
            print("\nShaders not compiled/linked properly")
            result = -1
        else:
            result = glGetUniformLocationARB( self.__shaderProgramID, variableName)
            self.__checkOpenGLError( )
        if result < 0:
            print('Variable "%s" not known to the shader' %  variableName )
            sys.exit( )
        else:
            return result

    def indexOfVertexAttribute( self, attributeName ):
        """Find the index of an attribute variable."""
        if not self.__programReady:
            print("\nShaders not compiled/linked properly")
            result = -1
        else:
            result = glGetAttribLocationARB( self.__shaderProgramID, attributeName )
            self.__checkOpenGLError( )
        if result < 0:
            print('Attribute "%s" not known to the shader' % attributeName )
            sys.exit( )
        else:
            return result
    
    def isEnabled( self ):
        return self.__isEnabled

if __name__ == '__main__':

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "rage.glsl"

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    glutInitWindowSize( width, height )
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH)-width)//2, (glutGet(GLUT_SCREEN_HEIGHT)-height)//2);
    glutCreateWindow("shadertoy")

    init()

    Sp = ShaderProgram()
    Sp.addShader(GL_FRAGMENT_SHADER_ARB, filename)
    Sp.linkShaders()
    Sp.enable()

    start_time = time.time()

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse);
    glutMotionFunc(motion);
    glutReshapeFunc(reshape);
    glutIdleFunc(animation)
    glutMainLoop()

