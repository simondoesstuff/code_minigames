from ipycanvas import RoughCanvas, hold_canvas
from ipywidgets import Image
import random
from math import pi

class Snake():
    # intentionally exposed to allow "cheating"
    score = 0
    win_state = 'running'

    def __init__(self, dim: int = 300, n: int = 10):
        self.canvas = RoughCanvas(width=dim, height=dim * 1.15)
        self.n = n
        self.dim = dim
        self._tail = list(reversed([(n//2 - i, n//2) for i in range(3)]))
        self._full = set(self._tail)
        
        self._sprites = {
            'apple': Image.from_file('sprites/apple.png')
        }
        
        self._gradient = self.canvas.create_linear_gradient(
            0, 0,
            dim, dim,
            [
                (0, "red"),
                (1 / 6, "orange"),
                (2 / 6, "yellow"),
                (3 / 6, "green"),
                (4 / 6, "blue"),
                (5 / 6, "#4B0082"),
                (1, "violet"),
            ],
        )
        
        self._newApple()
        self._draw()
    
    def _newApple(self):
        if (self.n ** 2 - len(self._full)) <= 1:
            self.win_state = 'won'
            return

        while True:
            r = lambda: random.randint(0, self.n - 1)
            self._apple = (r(), r())
            if self._apple not in self._full:
                break
    
    def _step(self, dir: (int, int)):
        head = self._tail[-1]
        next_step = (head[0] + dir[0], head[1] + dir[1])
        next_step = (next_step[0] % self.n, next_step[1] % self.n) # wrap around

        if next_step in self._full:
            self.win_state = 'lost'
            return
        
        if next_step == self._apple:
            self._newApple()
            self.score += 1
        else:
            self._full.remove(self._tail[0])
            self._tail.pop(0) # shift
        
        self._tail.append(next_step)
        self._full.add(next_step)
    
    def forward(self):
        if self.win_state != 'running':
            return
        head = self._tail[-1]
        neck = self._tail[-2]
        orientation = (head[0] - neck[0], head[1] - neck[1])
        self._step(orientation)
        self._draw()
    
    def left(self):
        if self.win_state != 'running':
            return
        head = self._tail[-1]
        neck = self._tail[-2]
        orientation = (head[0] - neck[0], head[1] - neck[1])
        self._step((orientation[1], -orientation[0]))
        self._draw()
    
    def right(self):
        if self.win_state != 'running':
            return
        head = self._tail[-1]
        neck = self._tail[-2]
        orientation = (head[0] - neck[0], head[1] - neck[1])
        self._step((-orientation[1], orientation[0]))
        self._draw()
    
    def _draw(self):
        canvas, n, dim = self.canvas, self.n, self.dim
        
        with hold_canvas(canvas):
            canvas.clear()
            canvas.save()
            
            if self.win_state == 'running':
                color = 'black'
            elif self.win_state == 'won':
                color = 'green'
            elif self.win_state == 'lost':
                color = 'red'
            else:
                raise Exception('Invalid win state', self.win_state)
            
            canvas.fill_style = color
            canvas.stroke_style = color
            
            # grid lines
            canvas.line_width = 1
            canvas.global_alpha = 0.4
            grid_size = self.dim // n
            for i in range(n):
                canvas.begin_path()
                canvas.move_to(i * grid_size, 0)
                canvas.line_to(i * grid_size, dim)
                canvas.stroke()
                canvas.begin_path()
                canvas.move_to(0, i * grid_size)
                canvas.line_to(dim, i * grid_size)
                canvas.stroke()
                
            # snake
            canvas.save()
            canvas.global_alpha = 1
            canvas.line_width = grid_size * 0.8
            canvas.line_join = 'round'
            canvas.line_cap = 'round'
            canvas.stroke_style = self._gradient
            x_0, y_0 = self._tail[0]
            canvas.begin_path()
            for i, (x, y) in enumerate(self._tail):
                # center
                x += .5
                y += .5
                # wiggle
                x += (random.random() - .5) * .3
                y += (random.random() - .5) * .3

                if i == 0:
                    canvas.move_to(x * grid_size, y * grid_size)
                else:
                    if abs(x - x_0 - 0.5) > 2 or abs(y - y_0 - 0.5) > 2:
                        canvas.stroke()
                        canvas.begin_path()
                        canvas.move_to(x * grid_size, y * grid_size)

                canvas.line_to(x * grid_size, y * grid_size)
                x_0, y_0 = x, y

            canvas.stroke()
            canvas.restore()
            
            # background
            canvas.rough_fill_style = 'hachure'
            canvas.global_alpha = 0.2
            canvas.fill_rect(0, 0, dim, dim)
            
            # border
            canvas.global_alpha = 1
            canvas.line_width = 5
            canvas.stroke_rect(0, 0, dim, dim)
            
            # apple
            apple_loc = (self._apple[0] * grid_size, self._apple[1] * grid_size)
            canvas.draw_image(self._sprites['apple'], *apple_loc, grid_size, grid_size)
            
            # score
            canvas.font = '30px serif'
            canvas.fill_text(str(self.score), dim // 2 - 10, dim * 1.1)
            
            # eyes
            canvas.save()
            canvas.rough_fill_style = 'solid'
            canvas.fill_style = 'white'
            neck = self._tail[-2]
            head = self._tail[-1]
            orientation = (head[0] - neck[0], head[1] - neck[1])
            
            def draw_eye(x, y):
                canvas.save()
                canvas.translate((x + .5) * grid_size, (y + .5) * grid_size)
                canvas.rotate(-pi / 2 + pi / 4 * orientation[0] + pi / 4 * orientation[1])
                canvas.fill_circle(0, 0, grid_size * 0.1)
                canvas.restore()
            
            draw_eye(head[0] - .2, head[1])
            draw_eye(head[0] + .2, head[1])
            canvas.restore()
            
            canvas.restore()
