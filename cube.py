import math
import time
import warnings
warnings.filterwarnings("ignore")
import numpy as np
from bruhanimate.bruhscreen import Screen
from bruhanimate.bruhffer import Buffer
from bruhcolor import bruhcolored as colored

PROJECTION_MATRIX = np.matrix([
     [1, 0, 0],
     [0, 1, 0],
     [0, 0, 0]
])

def get_z_rotation_matrix(angle):
    return np.matrix([
        [math.cos(angle), -math.sin(angle), 0],
        [math.sin(angle), math.cos(angle), 0],
        [0, 0, 1]
    ])

def get_y_rotation_matrix(angle):
    return np.matrix([
        [math.cos(angle), 0, math.sin(angle)],
        [0, 1, 0],
        [-math.sin(angle), 0, math.cos(angle)]
    ])

def get_x_rotation_matrix(angle):
    return np.matrix([
        [1, 0, 0],
        [0, math.cos(angle), -math.sin(angle)],
        [0, math.sin(angle), math.cos(angle)],
    ])

def connect_points(x0, y0, x1, y1, buffer, char=None):
    if ((x0 < 0 and x1) < 0 or (x0 >= buffer.width() * 2 and x1 > buffer.width() * 2)
            or (y0 < 0 and y1 < 0) or (y0 >= buffer.height() * 2 and y1 >= buffer.height() * 2)):
        return

    line_chars = " ''^.|/7.\\|Ywbd#"
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    cx = -1 if x0 > x1 else 1
    cy = -1 if y0 > y1 else 1

    def get_start(x, y):
        c = buffer.get_char(x, y)
        if c is not None:
            return line_chars.find(c)
        return 0

    def x_draw(ix, iy):
        err = dx
        px = ix - 2
        py = iy - 2
        next_char = 0
        while ix != x1:
            if ix < px or ix - px >= 2 or iy < py or iy - py >= 2:
                px = ix & ~1
                py = iy & ~1
                next_char = get_start(px, py)
            next_char |= 2 ** abs(ix % 2) * 4 ** (iy % 2)
            err -= 2 * dy
            if err < 0:
                iy += cy
                err += 2 * dx
            ix += cx

            if char is None:
                buffer.put_char(
                    px, py, line_chars[next_char])
            else:
                buffer.put_char(px, py, char)


    def y_draw(ix, iy):
        err = dy
        px = ix - 2
        py = iy - 2
        next_char = 0

        while iy != y1:
            if ix < px or ix - px >= 2 or iy < py or iy - py >= 2:
                px = ix & ~1
                py = iy & ~1
                next_char = get_start(px, py)
            next_char |= 2 ** abs(ix % 2) * 4 ** (iy % 2)
            err -= 2 * dx
            if err < 0:
                ix += cx
                err += 2 * dy
            iy += cy

            if char is None:
                buffer.put_char(
                    px, py, line_chars[next_char])
            else:
                buffer.put_char(px, py, char)
    if dx > dy:
        x_draw(x0, y0+1)
    else:
        y_draw(x0+1, y0)


def do_cube(back_buffer, points, origin, CUBE_SIZE, Z_ANGLE, Y_ANGLE, X_ANGLE):
    projected_points = []

    for point in points:

        _2d_rotation = np.dot(get_z_rotation_matrix(Z_ANGLE), point.reshape(3, 1))

        _2d_rotation = np.dot(get_y_rotation_matrix(Y_ANGLE), _2d_rotation)

        _2d_rotation = np.dot(get_x_rotation_matrix(X_ANGLE), _2d_rotation)

        _2d_projection = np.dot(PROJECTION_MATRIX, _2d_rotation)

        x = int(_2d_projection[0][0] * CUBE_SIZE) + origin[0]

        y = int(_2d_projection[1][0] * CUBE_SIZE) + origin[1]

        projected_points.append((x, y))

    Z_ANGLE += 0.1
    Y_ANGLE += 0.1
    X_ANGLE += 0.1

    CHAR = None

    for p in range(4):
        connect_points(
            projected_points[p][0],
            projected_points[p][1],
            projected_points[(p+1)%4][0],
            projected_points[(p+1)%4][1],
            back_buffer,
            char=CHAR
        )

        connect_points(
            projected_points[p+4][0],
            projected_points[p+4][1],
            projected_points[((p+1)%4)+4][0],
            projected_points[((p+1)%4)+4][1],
            back_buffer,
            char=CHAR
        )

        connect_points(
            projected_points[p][0],
            projected_points[p][1],
            projected_points[p+4][0],
            projected_points[p+4][1],
            back_buffer,
            char=CHAR
        )


def main(screen):

    CUBE_SIZE = 75

    dCUBE = -1

    points = []
    points.append(np.matrix([-1, -1, 1]))
    points.append(np.matrix([1, -1, 1]))
    points.append(np.matrix([1, 1, 1]))
    points.append(np.matrix([-1, 1, 1]))
    points.append(np.matrix([-1, -1, -1]))
    points.append(np.matrix([1, -1, -1]))
    points.append(np.matrix([1, 1, -1]))
    points.append(np.matrix([-1, 1, -1]))

    Z_ANGLE = 0
    Y_ANGLE = 0
    X_ANGLE = 0

    back_buffer    = Buffer(screen.height, screen.width)

    display_buffer = Buffer(screen.height, screen.width)

    cube_1_origin = (display_buffer.width() // 2, display_buffer.height() // 2)
    cube_2_origin = (display_buffer.width() // 2 + 60, display_buffer.height() // 2)
    cube_3_origin = (display_buffer.width() // 2 - 60, display_buffer.height() // 2)
    cube_4_origin = (display_buffer.width() // 2 + 110, display_buffer.height() // 2)
    cube_5_origin = (display_buffer.width() // 2 - 110, display_buffer.height() // 2)

    try:

        while True:

            Z_ANGLE += 0.01
            Y_ANGLE += 0.01
            X_ANGLE += 0.01

            do_cube(
                back_buffer=back_buffer,
                points=points,
                origin=cube_1_origin,
                CUBE_SIZE=25,
                Z_ANGLE=Z_ANGLE,
                Y_ANGLE=Y_ANGLE,
                X_ANGLE=X_ANGLE
            )

            do_cube(
                back_buffer=back_buffer,
                points=points,
                origin=cube_1_origin,
                CUBE_SIZE=10,
                Z_ANGLE=-Z_ANGLE,
                Y_ANGLE=-Y_ANGLE,
                X_ANGLE=-X_ANGLE
            )
            
            do_cube(
                back_buffer=back_buffer,
                points=points,
                origin=cube_2_origin,
                CUBE_SIZE=10,
                Z_ANGLE=-Z_ANGLE,
                Y_ANGLE=-Y_ANGLE,
                X_ANGLE=X_ANGLE
            )

            do_cube(
                back_buffer=back_buffer,
                points=points,
                origin=cube_3_origin,
                CUBE_SIZE=10,
                Z_ANGLE=-Z_ANGLE,
                Y_ANGLE=-Y_ANGLE,
                X_ANGLE=X_ANGLE
            )

            do_cube(
                back_buffer=back_buffer,
                points=points,
                origin=cube_4_origin,
                CUBE_SIZE=10,
                Z_ANGLE=Z_ANGLE,
                Y_ANGLE=Y_ANGLE,
                X_ANGLE=-X_ANGLE
            )

            do_cube(
                back_buffer=back_buffer,
                points=points,
                origin=cube_5_origin,
                CUBE_SIZE=10,
                Z_ANGLE=Z_ANGLE,
                Y_ANGLE=Y_ANGLE,
                X_ANGLE=-X_ANGLE
            )
            
            for x, y, val in display_buffer.get_buffer_changes(back_buffer):
                # val = colored(val, 196, attrs=["blink"]).colored
                screen.print_at(val, y, x, 1)
            
            display_buffer.sync_with(back_buffer)

            back_buffer.clear_buffer(val=" ")

    except KeyboardInterrupt:
        pass
   
    input()

if __name__ == "__main__":
    Screen.show(main)


