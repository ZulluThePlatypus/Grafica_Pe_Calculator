import pygame
import numpy as np
import glm
import os
from OpenGL.GL import *
from OpenGL.GLU import *

# --- CONFIGURARE ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# --- UTILITARE SHADER ---
def load_shader(shader_file):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, shader_file)
    with open(file_path, 'r') as file:
        return file.read()

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    success = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not success:
        raise Exception(glGetShaderInfoLog(shader).decode('utf-8'))
    return shader

def create_shader_program(vs_file, fs_file):
    vs = compile_shader(load_shader(vs_file), GL_VERTEX_SHADER)
    fs = compile_shader(load_shader(fs_file), GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)
    glDeleteShader(vs)
    glDeleteShader(fs)
    return program

# --- GEOMETRIE ---
cube_vertices = np.array([
    # Pozitii          # Normale
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
     0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
    -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,

    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
     0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
     0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
     0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
    -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,

    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,
    -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,
    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,

     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,
     0.5,  0.5, -0.5,  1.0,  0.0,  0.0,
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
     0.5, -0.5,  0.5,  1.0,  0.0,  0.0,
     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,

    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
     0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
    -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,

    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
     0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
    -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0
], dtype=np.float32)

plane_vertices = np.array([
    -100.0, 0.0, -100.0,  0.0,  1.0,  0.0,
     100.0, 0.0, -100.0,  0.0,  1.0,  0.0,
     100.0, 0.0,  100.0,  0.0,  1.0,  0.0,
     100.0, 0.0,  100.0,  0.0,  1.0,  0.0,
    -100.0, 0.0,  100.0,  0.0,  1.0,  0.0,
    -100.0, 0.0, -100.0,  0.0,  1.0,  0.0
], dtype=np.float32)

def setup_vao(data):
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)
    return vao, len(data) // 6

# --- SISTEM TEXT 2D (CERINTA 7 - UI) ---
class TextRenderer:
    def __init__(self):
        self.font = pygame.font.SysFont('Arial', 30, bold=True)

    def draw_text(self, text, x, y):
        # Randam textul pe o suprafata Pygame
        text_surface = self.font.render(text, True, (255, 255, 255, 255), (0, 0, 0, 0))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        width, height = text_surface.get_width(), text_surface.get_height()

        # Cream o textura OpenGL temporara
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        # Trecem in mod 2D (Orthographic)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Desenam Quad-ul cu textul
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + width, y)
        glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
        glTexCoord2f(0, 1); glVertex2f(x, y + height)
        glEnd()
        
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        
        # Revenim la 3D
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glDeleteTextures(1, [texture_id])

# --- OBIECTE JOC ---
class Wall:
    def __init__(self, x, z, width, length, color=(0.6, 0.6, 0.6)):
        self.pos = glm.vec3(x, 0.5, z) 
        self.scale = glm.vec3(width, 1.0, length)
        self.color = color
        self.min_x = x - width / 2
        self.max_x = x + width / 2
        self.min_z = z - length / 2
        self.max_z = z + length / 2

class Collectible:
    def __init__(self, x, z):
        self.pos = glm.vec3(x, 0.5, z)
        self.active = True
        self.rotation = 0.0
    
    def update(self, dt):
        self.rotation += 90.0 * dt # Se roteste constant

class Car:
    def __init__(self):
        self.pos = glm.vec3(0.0, 0.5, 0.0)
        self.velocity = 0.0
        self.rotation = 0.0
        self.score = 0
        self.boost_timer = 0.0

    def update(self, dt, keys, walls, collectibles):
        # Boost logic
        max_speed = 30.0 if self.boost_timer <= 0 else 50.0
        if self.boost_timer > 0: self.boost_timer -= dt
        
        acc = 15.0
        if keys[pygame.K_w]: self.velocity += acc * dt
        elif keys[pygame.K_s]: self.velocity -= acc * dt
        else: self.velocity -= np.sign(self.velocity) * 5.0 * dt
            
        self.velocity = max(min(self.velocity, max_speed), -10.0)

        if abs(self.velocity) > 0.1:
            direction = 1 if self.velocity > 0 else -1
            turn_speed = 100.0 * dt * direction
            if keys[pygame.K_a]: self.rotation += turn_speed
            if keys[pygame.K_d]: self.rotation -= turn_speed

        # Miscare
        rad = np.radians(self.rotation)
        new_x = self.pos.x + np.sin(rad) * self.velocity * dt
        new_z = self.pos.z + np.cos(rad) * self.velocity * dt

        # Coliziune Pereti
        collision = False
        for w in walls:
            if (new_x + 0.4 > w.min_x and new_x - 0.4 < w.max_x and
                new_z + 0.4 > w.min_z and new_z - 0.4 < w.max_z):
                collision = True
                break
        
        if collision:
            self.velocity = -self.velocity * 0.5
        else:
            self.pos.x, self.pos.z = new_x, new_z

        # Coliziune Colectabile (Cerinta 6)
        for c in collectibles:
            if c.active:
                dist = glm.distance(self.pos, c.pos)
                if dist < 1.5: # Daca suntem aproape
                    c.active = False
                    self.score += 1
                    self.boost_timer = 2.0 # Boost 2 secunde

# --- MAIN ---
shader_program = None

def draw_mesh(vao, count, model, color, shininess):
    glUniformMatrix4fv(glGetUniformLocation(shader_program, "model"), 1, GL_FALSE, glm.value_ptr(model))
    glUniform3fv(glGetUniformLocation(shader_program, "objectColor"), 1, glm.value_ptr(glm.vec3(color)))
    glUniform1f(glGetUniformLocation(shader_program, "shininess"), shininess)
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, count)

def main():
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Joc Final - UI si Colectabile")

    global shader_program
    try:
        shader_program = create_shader_program('vertex_shader.glsl', 'fragment_shader.glsl')
    except: return

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.5, 0.7, 1.0, 1.0) 

    cube_vao, cube_count = setup_vao(cube_vertices)
    plane_vao, plane_count = setup_vao(plane_vertices)
    
    text_renderer = TextRenderer()
    car = Car()
    
    # Pereti
    walls = [
        Wall(0, -50, 100, 2), Wall(0, 50, 100, 2),
        Wall(-50, 0, 2, 100), Wall(50, 0, 2, 100),
        Wall(0, 0, 20, 20, (0.4, 0.4, 0.4)) # Obstacol central
    ]
    
    # Colectabile (Cerinta 6 - Minim 3 obiecte interactive)
    collectibles = [
        Collectible(0, -30),
        Collectible(-30, 0),
        Collectible(30, 0),
        Collectible(0, 30)
    ]

    projection = glm.perspective(glm.radians(45), SCREEN_WIDTH/SCREEN_HEIGHT, 0.1, 200.0)
    clock = pygame.time.Clock()
    start_ticks = pygame.time.get_ticks()

    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); return

        # Update
        car.update(dt, pygame.key.get_pressed(), walls, collectibles)
        for c in collectibles: c.update(dt)

        # Draw 3D
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader_program)

        rad = np.radians(car.rotation)
        cam_x = car.pos.x - np.sin(rad) * 12.0
        cam_z = car.pos.z - np.cos(rad) * 12.0
        view = glm.lookAt(glm.vec3(cam_x, 6.0, cam_z), car.pos, glm.vec3(0, 1, 0))

        glUniformMatrix4fv(glGetUniformLocation(shader_program, "projection"), 1, GL_FALSE, glm.value_ptr(projection))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUniform3fv(glGetUniformLocation(shader_program, "lightPos"), 1, glm.value_ptr(glm.vec3(50, 100, 50)))
        glUniform3fv(glGetUniformLocation(shader_program, "ambientColor"), 1, glm.value_ptr(glm.vec3(0.3)))
        glUniform3fv(glGetUniformLocation(shader_program, "lightColor"), 1, glm.value_ptr(glm.vec3(1.0)))
        glUniform3fv(glGetUniformLocation(shader_program, "viewPos"), 1, glm.value_ptr(glm.vec3(cam_x, 6.0, cam_z)))

        draw_mesh(plane_vao, plane_count, glm.mat4(1.0), (0.2, 0.6, 0.2), 1.0)
        for w in walls:
            m = glm.translate(glm.mat4(1.0), w.pos)
            m = glm.scale(m, w.scale)
            draw_mesh(cube_vao, cube_count, m, w.color, 16.0)

        # Desenam Colectabilele (cuburi rotitoare aurii)
        for c in collectibles:
            if c.active:
                m = glm.translate(glm.mat4(1.0), c.pos)
                m = glm.rotate(m, glm.radians(c.rotation), glm.vec3(0, 1, 0))
                m = glm.rotate(m, glm.radians(45), glm.vec3(1, 0, 0)) # Rotit pe colt
                draw_mesh(cube_vao, cube_count, m, (1.0, 0.8, 0.0), 128.0) # Auriu

        # Desenam Masina
        m = glm.translate(glm.mat4(1.0), car.pos)
        m = glm.rotate(m, glm.radians(car.rotation), glm.vec3(0, 1, 0))
        m = glm.scale(m, glm.vec3(1.0, 0.5, 2.0))
        color = (1.0, 0.2, 0.2) if car.boost_timer <= 0 else (0.2, 1.0, 1.0) # Rosu normal, Cyan cand e boost
        draw_mesh(cube_vao, cube_count, m, color, 64.0)

        glUseProgram(0) # Oprim shaderul 3D pentru a desena UI-ul

        # Draw UI (Cerința 7 - HUD)
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        text_renderer.draw_text(f"Scor: {car.score}/{len(collectibles)}", 20, SCREEN_HEIGHT - 50)
        text_renderer.draw_text(f"Timp: {seconds}s", 20, SCREEN_HEIGHT - 90)
        
        if car.score == len(collectibles):
            text_renderer.draw_text("AI CASTIGAT!", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2)

        pygame.display.flip()

if __name__ == "__main__":
    main()