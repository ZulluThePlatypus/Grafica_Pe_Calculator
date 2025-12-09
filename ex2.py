import glfw
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader



vertex_shader = """
#version 330 core
layout(location = 0) in vec3 position;

void main()
{
    gl_Position = vec4(position, 1.0);
}
"""

fragment_shader = """
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(2.0, 1.5, 0.2, 1.0);
}
"""
def main():
    if not glfw.init():
        return
    
    window = f=glfw.create_window(800, 600, "Laborator 1 - Primul triunghi", None, None)

    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)

   

    vertices=np.array([
        -0.8, 0.5, 0.0,    
        -1.0, -0.2, 0.0, 
        -0.6, -0.2, 0.0,   

       
        0.0, 0.5, 0.0,     
        0.0, -0.5, 0.0,    
        1.0, 0.5, 0.0,     

        0.0, -0.5, 0.0,    
        1.0, -0.5, 0.0,   
        1.0, 0.5, 0.0      
    ], dtype=np.float32)

    VAO=glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO=glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
   
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    
    vshader = compileShader(vertex_shader, GL_VERTEX_SHADER) 
    fshader = compileShader(fragment_shader, GL_FRAGMENT_SHADER) 
    
    program = glCreateProgram()
    glAttachShader(program, vshader) 
    glAttachShader(program, fshader) 
    glLinkProgram(program) 
    
    
    while not glfw.window_should_close(window):
        
       
        glClear(GL_COLOR_BUFFER_BIT)
        
       
        glUseProgram(program)
        
      
        glBindVertexArray(VAO)
      
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glDrawArrays(GL_TRIANGLES, 3, 6)
      
        glfw.swap_buffers(window)
        
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()