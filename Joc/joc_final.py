import pygame
import numpy as np
import glm
from OpenGL.GL import *
from OpenGL.GLU import *

# --- CONFIGURARE ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 10.0 # Pista foarte larga

# --- SHADERS (GLSL INTEGRAT) ---
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 FragPos;
out vec3 Normal;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;
in vec3 FragPos;
in vec3 Normal;

uniform vec3 objectColor;
uniform vec3 lightPos;
uniform vec3 viewPos;

void main()
{
    float ambientStrength = 0.4;
    vec3 ambient = ambientStrength * vec3(1.0, 1.0, 1.0);
    
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * vec3(1.0, 1.0, 1.0);
    
    float specularStrength = 0.3;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);  
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * vec3(1.0, 1.0, 1.0);  
    
    vec3 result = (ambient + diffuse + specular) * objectColor;
    FragColor = vec4(result, 1.0);
}
"""

def create_shader():
    vs = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vs, VERTEX_SHADER)
    glCompileShader(vs)
    if not glGetShaderiv(vs, GL_COMPILE_STATUS): raise Exception(glGetShaderInfoLog(vs).decode())
    fs = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fs, FRAGMENT_SHADER)
    glCompileShader(fs)
    if not glGetShaderiv(fs, GL_COMPILE_STATUS): raise Exception(glGetShaderInfoLog(fs).decode())
    prog = glCreateProgram()
    glAttachShader(prog, vs); glAttachShader(prog, fs); glLinkProgram(prog)
    return prog

# --- GEOMETRIE CUB ---
cube_vertices = np.array([
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
    -0.5,  0.5, -0.5,  0.0,  0.0, -1.0, -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0, 0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
     0.5,  0.5,  0.5,  0.0,  0.0,  1.0, 0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
    -0.5,  0.5,  0.5,  0.0,  0.0,  1.0, -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0, -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0, -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5,  0.5, -1.0,  0.0,  0.0, -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,
     0.5,  0.5,  0.5,  1.0,  0.0,  0.0, 0.5,  0.5, -0.5,  1.0,  0.0,  0.0,
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0, 0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
     0.5, -0.5,  0.5,  1.0,  0.0,  0.0, 0.5,  0.5,  0.5,  1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0, 0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0, 0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
    -0.5, -0.5,  0.5,  0.0, -1.0,  0.0, -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0, 0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0, 0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
    -0.5,  0.5,  0.5,  0.0,  1.0,  0.0, -0.5,  0.5, -0.5,  0.0,  1.0,  0.0
], dtype=np.float32)

def setup_vao():
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)
    return vao

# --- HARTA CIRCUITULUI (CONTINUU - LOOP) ---
# 1 = Zid/Parapet (Rosu/Alb)
# 0 = Asfalt (Gri)
# S = Linie Start
# Pista are 4 blocuri latime. Urmareste zerourile '0'.
TRACK_MAP = [
    "1111111111111111111111111111111111111111111",
    "1111111111111100000000011111100000000000001", # Back Straight Top
    "1111111111111100000000011111100000000000001",
    "1111111111111100001100011111110000111111111", 
    "1111111111111100001100011111110000111111111",
    "1111111100000000001100011111110000111111111", # Turn 9 Area
    "1111111100000000001100000000000000111111111",
    "1111111100011111111100000000000000111111111",
    "1111111100011111111111111111110000111111111",
    "1111111100000000000001111111110000111111111", 
    "1111111100000000000001111111110000111111111",
    "1111111111111111000001111111110000111111111",
    "1111111111111111000001111111110000000000001", # Turn 3 (Long Right)
    "1111111111111111000001111111110000000000001",
    "1111111111111111000001111111111111111110001",
    "1111111111111111000001111111111111111110001",
    "1111111111111111000001111111111111111110001",
    "10000000000000000000011111111111111111110001", # Final Turn leading to straight
    "1000000000000000000001111111111111111110001",
    "1000011111111111111111111111111111111110001",
    "1000011111111111111111111111111111111110001", # Turn 1
    "1000000000000000000000000SS0000000000000001", # MAIN STRAIGHT
    "1000000000000000000000000SS0000000000000001",
    "1000000000000000000000000SS0000000000000001",
    "1111111111111111111111111111111111111111111"
]

class Car:
    def __init__(self, start_x, start_z):
        self.pos = glm.vec3(start_x, 0.2, start_z)
        self.vel = 0.0
        self.rot = 90.0 # Orientat spre Est (in lungul liniei de start)
        self.width = 1.0
        self.length = 2.0

    def draw(self, vao, shader):
        # --- Masina F1 ---
        # Corp
        self._draw_part(vao, shader, (0, 0.3, 0), (1.2, 0.4, 4.0), (0.9, 0.1, 0.1)) 
        # Cockpit
        self._draw_part(vao, shader, (0, 0.5, -0.5), (0.8, 0.4, 1.2), (0.1, 0.1, 0.1))
        # Eleron Spate
        self._draw_part(vao, shader, (0, 0.9, -1.9), (2.2, 0.1, 0.8), (1.0, 1.0, 1.0))
        # Eleron Fata
        self._draw_part(vao, shader, (0, 0.2, 2.0), (2.2, 0.1, 0.8), (1.0, 1.0, 1.0))
        # Roti
        wc = (0.15, 0.15, 0.15)
        self._draw_part(vao, shader, (-0.9, 0.3, -1.4), (0.6, 0.9, 0.9), wc)
        self._draw_part(vao, shader, ( 0.9, 0.3, -1.4), (0.6, 0.9, 0.9), wc)
        self._draw_part(vao, shader, (-0.9, 0.3, 1.4), (0.5, 0.9, 0.9), wc)
        self._draw_part(vao, shader, ( 0.9, 0.3, 1.4), (0.5, 0.9, 0.9), wc)

    def _draw_part(self, vao, shader, offset, scale, color):
        model = glm.translate(glm.mat4(1.0), self.pos)
        model = glm.rotate(model, glm.radians(self.rot), glm.vec3(0, 1, 0))
        model = glm.translate(model, glm.vec3(offset))
        model = glm.scale(model, glm.vec3(scale))
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniform3fv(glGetUniformLocation(shader, "objectColor"), 1, glm.value_ptr(glm.vec3(color)))
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, 36)

    def update(self, dt, keys, walls):
        acc = 40.0
        if keys[pygame.K_w]: self.vel += acc * dt
        elif keys[pygame.K_s]: self.vel -= acc * dt
        else: self.vel -= np.sign(self.vel) * 15.0 * dt
        self.vel = max(min(self.vel, 70.0), -20.0)
        
        if abs(self.vel) > 0.1:
            turn = 120.0 * dt * (1 if self.vel > 0 else -1)
            if keys[pygame.K_a]: self.rot += turn
            if keys[pygame.K_d]: self.rot -= turn
        
        rad = np.radians(self.rot)
        next_x = self.pos.x + np.sin(rad) * self.vel * dt
        next_z = self.pos.z + np.cos(rad) * self.vel * dt
        
        # Coliziune
        collision = False
        box = (next_x - 0.5, next_x + 0.5, next_z - 0.5, next_z + 0.5)
        for w in walls:
            if (box[1] > w[0] and box[0] < w[1] and box[3] > w[2] and box[2] < w[3]):
                collision = True; break
        
        if collision: self.vel *= -0.5
        else: self.pos.x, self.pos.z = next_x, next_z

def main():
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Endless Circuit F1")
    try: shader = create_shader()
    except Exception as e: print(e); return
    glEnable(GL_DEPTH_TEST); glClearColor(0.53, 0.81, 0.98, 1.0)
    vao = setup_vao()
    
    walls, floor, finish = [], [], []
    start_pos = (0,0)
    
    rows = len(TRACK_MAP)
    cols = max(len(row) for row in TRACK_MAP)
    
    for r in range(rows):
        row_str = TRACK_MAP[r]
        for c in range(len(row_str)):
            wx, wz = c * TILE_SIZE, r * TILE_SIZE
            char = row_str[c]
            if char == '1': # Parapet
                walls.append((wx - TILE_SIZE/2, wx + TILE_SIZE/2, wz - TILE_SIZE/2, wz + TILE_SIZE/2, wx, wz))
            elif char == '0': # Asfalt
                floor.append((wx, wz))
            elif char == 'S': # Start
                finish.append((wx, wz))
                if start_pos == (0,0): start_pos = (wx, wz)

    car = Car(start_pos[0], start_pos[1])
    clock = pygame.time.Clock()
    projection = glm.perspective(glm.radians(60), SCREEN_WIDTH/SCREEN_HEIGHT, 0.1, 500.0)

    while True:
        dt = clock.tick(FPS) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE): pygame.quit(); return

        car.update(dt, pygame.key.get_pressed(), walls)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader)
        
        rad = np.radians(car.rot)
        cam_x = car.pos.x - np.sin(rad) * 12.0
        cam_z = car.pos.z - np.cos(rad) * 12.0
        view = glm.lookAt(glm.vec3(cam_x, 8.0, cam_z), car.pos, glm.vec3(0, 1, 0))
        
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUniform3fv(glGetUniformLocation(shader, "lightPos"), 1, glm.value_ptr(glm.vec3(50, 100, 50)))
        glUniform3fv(glGetUniformLocation(shader, "viewPos"), 1, glm.value_ptr(glm.vec3(cam_x, 8.0, cam_z)))

        # IARBA
        m = glm.translate(glm.mat4(1.0), glm.vec3(200, -0.1, 200))
        m = glm.scale(m, glm.vec3(800.0, 0.1, 800.0))
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(m))
        glUniform3fv(glGetUniformLocation(shader, "objectColor"), 1, glm.value_ptr(glm.vec3(0.1, 0.8, 0.1))) 
        glBindVertexArray(vao); glDrawArrays(GL_TRIANGLES, 0, 36)

        # PARAPETI
        for w in walls:
            m = glm.translate(glm.mat4(1.0), glm.vec3(w[4], 0.1, w[5]))
            m = glm.scale(m, glm.vec3(TILE_SIZE, 0.2, TILE_SIZE))
            glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(m))
            col = (0.9, 0.1, 0.1) if (int(w[4]/TILE_SIZE) + int(w[5]/TILE_SIZE)) % 2 == 0 else (1.0, 1.0, 1.0)
            glUniform3fv(glGetUniformLocation(shader, "objectColor"), 1, glm.value_ptr(glm.vec3(col)))
            glDrawArrays(GL_TRIANGLES, 0, 36)

        # ASFALT
        for f in floor:
            m = glm.translate(glm.mat4(1.0), glm.vec3(f[0], 0.0, f[1]))
            m = glm.scale(m, glm.vec3(TILE_SIZE, 0.1, TILE_SIZE))
            glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(m))
            glUniform3fv(glGetUniformLocation(shader, "objectColor"), 1, glm.value_ptr(glm.vec3(0.25, 0.25, 0.25)))
            glDrawArrays(GL_TRIANGLES, 0, 36)

        # FINISH LINE
        for f in finish:
            m = glm.translate(glm.mat4(1.0), glm.vec3(f[0], 0.02, f[1]))
            m = glm.scale(m, glm.vec3(TILE_SIZE, 0.1, TILE_SIZE))
            glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(m))
            is_black = (int(f[0]/TILE_SIZE) + int(f[1]/TILE_SIZE)) % 2 == 0 
            col = (0.1, 0.1, 0.1) if is_black else (1.0, 1.0, 1.0)
            glUniform3fv(glGetUniformLocation(shader, "objectColor"), 1, glm.value_ptr(glm.vec3(col)))
            glDrawArrays(GL_TRIANGLES, 0, 36)

        car.draw(vao, shader)
        pygame.display.flip()

if __name__ == "__main__":
    main()