#!/usr/bin/env python3

# see http://www.iquilezles.org/apps/shadertoy/

import sys
import array
import random
import time
import struct
import glob

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

start_time = 0

width = 512
height = 512

# non-fullscreen window
ww, wh = width, height

# texture size
txw = 256
txh = 256

size = txw * txh
texture = 0
shader_body = ''
fullscreen = 0
buf = (GLuint * size)(0)
Sp = None
g_filename = ''

class ShaderProgram ( object ):
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
        for ext in extensions:
            if ( not ext ):
                print("Driver does not support ", ext)
                sys.exit()

    def __checkOpenGLError( self ):
        err = glGetError()
        if ( err != GL_NO_ERROR ):
            print('GLERROR: ', gluErrorString( err ))
            sys.exit()

    def reset(self):
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

    def addShader( self, shaderType, fileName ):
        shaderHandle = glCreateShaderObjectARB(shaderType)
        self.__checkOpenGLError( )

        global shader_body
        shader_body = open(fileName, 'r').read()

        header = "#version 300 es\nprecision mediump float;\n"
        footer = "out vec4 fragColor;\nvoid main() { mainImage(fragColor, gl_FragCoord.xy);}\n"

        s = ''

        if 'iResolution' in shader_body:
            s += 'uniform vec2 iResolution;\n'

        if 'iTime' in shader_body:
            s += 'uniform float iTime;\n'

        if 'iMouse' in shader_body:
            s += 'uniform vec4 iMouse;\n'

        if s != '':
            shader_body = header + s + shader_body

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

    def enable(self):
        if self.__programReady:
            glUseProgramObjectARB( self.__shaderProgramID )
            self.__isEnabled=True
            self.__checkOpenGLError( )
        else:
            print("Shaders not compiled/linked properly, enable() failed")

    def disable(self):
        glUseProgramObjectARB( 0 )
        self.__isEnabled=False
        self.__checkOpenGLError( )

    def indexOfUniformVariable( self, variableName ):
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


def togglefullscreen():
    global fullscreen,ww,wh

    if fullscreen:
        sw, sh = glutGet(GLUT_SCREEN_WIDTH), glutGet(GLUT_SCREEN_HEIGHT)
        glutPositionWindow((sw - ww) // 2, (sh - wh) // 2)
        glutReshapeWindow(ww, wh);
    else:
        glutFullScreen()

    glutPostRedisplay()
    fullscreen = not fullscreen

def reshape(w, h):
    global width, height
    width, height = w, h

    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0, 1, 1, 0, -1, 1);
    glMatrixMode(GL_MODELVIEW);

    for var in ('iResolution', 'resolution'):
        if 'uniform vec2 '+var in shader_body:
            glUniform2fvARB(Sp.indexOfUniformVariable(var), 1, struct.pack("ff", w, h))

def animation():
    ftime = time.time() - start_time

    for var in ('iTime', 'time'):
        if 'uniform float '+var in shader_body:
            glUniform1fvARB(Sp.indexOfUniformVariable(var), 1, struct.pack("f", ftime))

    glutPostRedisplay()

def init():
    global buf, texture

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)

    for y in range(txw):
        for x in range(txh):
            c = x ^ y
            buf[y*txw + x] = (c<<16)|(c<<8)|c

    data = array.array("I", buf).tobytes()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, txw, txh, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    glEnableClientState( GL_TEXTURE_COORD_ARRAY )
    glEnableClientState( GL_VERTEX_ARRAY )
    vertices = array.array('h', [0,0, 1,0, 0,1, 1,1])
    texcoord = array.array('f', [0,0, 1,0, 0,1, 1,1])
    glVertexPointer(2,GL_SHORT, 0, vertices.tobytes())
    glTexCoordPointer(2,GL_FLOAT, 0, texcoord.tobytes())

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glEnable(GL_TEXTURE_2D);

def display():
    glDisable(GL_DEPTH_TEST);
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    glutSwapBuffers()

def mouse(button, state, x, y):
    motion(x, y)

def motion(x, y):
    flx = x
    fly = height-y

    for var in ('iMouse', 'mouse'):
        if 'uniform vec4 '+var in shader_body:
            glUniform4fvARB(Sp.indexOfUniformVariable(var), 1, struct.pack("ffff", flx,fly,0,0))
        if 'uniform vec2 '+var in shader_body:
            glUniform4fvARB(Sp.indexOfUniformVariable(var), 1, struct.pack("ff", flx,fly))

def keyboard(key,x,y):
    if key==b'\x1b' or key==b'\x03':
        os._exit(0)
    elif key==b'f':
        togglefullscreen()

    glutPostRedisplay()

def load(filename):
    global Sp, g_filename, start_time

    if not os.path.exists(filename):
        return

    g_filename = filename

    start_time = time.time()
    Sp = ShaderProgram()
    Sp.addShader(GL_FRAGMENT_SHADER_ARB, filename)
    Sp.linkShaders()
    Sp.enable()

    reshape(width, height)

    path, name = os.path.split(filename)

    glutSetWindowTitle("pyshadertoy - %s" % name)

def load_near_file(step):
    global g_filename
    path, name = os.path.split(g_filename)
    files = glob.glob('*.glsl')
    i = files.index(name) if name in files else -1
    load(files[(len(files)+i+step)%len(files)])

def load_next_file():
    return load_near_file(+1)

def load_prev_file():
    return load_near_file(-1)

def special(key, x,y):
    global g_filename
    if key==GLUT_KEY_LEFT:
        load_prev_file()
    elif key==GLUT_KEY_RIGHT:
        load_next_file()

if __name__ == '__main__':

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "rage.glsl"

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH)-width)//2, (glutGet(GLUT_SCREEN_HEIGHT)-height)//2);
    glutCreateWindow("")

    init()
    start_time = time.time()

    load_next_file()

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse);
    glutMotionFunc(motion);
    glutReshapeFunc(reshape);
    glutIdleFunc(animation)
    glutSpecialFunc(special)
    glutMainLoop()

