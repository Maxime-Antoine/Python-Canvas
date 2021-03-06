"""
This module defines the canvas and the shape objects of the application
"""

from enum import Enum
from copy import deepcopy


class Canvas(object):
    """
    Represents a canvas of arbitrary size to draw on
    """
    def __init__(self, width, height):
        self.width = int(width)
        self.height = int(height)
        self.cells = [
            [(CanvasCellContentType.Empty, ' ')
             for i in range(self.width)]
            for j in range(self.height)
        ]
        self._previous_states = []

    def _draw_point(self, point):
        self.cells[point.x][point.y] = (CanvasCellContentType.Line, 'x')

    def _point_is_out_of_bound(self, point):
        x_is_out_of_canvas_bound = point.x < 0 or point.x >= self.width
        y_is_out_of_canvas_bound = point.y < 0 or point.y >= self.height
        return x_is_out_of_canvas_bound or y_is_out_of_canvas_bound

    def draw_line(self, line):
        """
        Draw a line on the canvas

        Args:
            line: the line to be drawn on the canvas
        """
        if (self._point_is_out_of_bound(line.from_point) or
            self._point_is_out_of_bound(line.to_point)):
            raise OutOfCanvasBoundError()
        self._save_state()
        self._draw_line(line)

    def _draw_line(self, line):
        for point in line.get_points():
            self._draw_point(point)

    def draw_rectangle(self, rectangle):
        """
        Draw a rectangle on the canvas

        Args:
            rectangle: the rectangle to be drawn on the canvas
        """
        if (self._point_is_out_of_bound(rectangle.top_left_point) or
            self._point_is_out_of_bound(rectangle.bottom_right_point)):
            raise OutOfCanvasBoundError()
        self._save_state()
        for line in rectangle.get_lines():
            self._draw_line(line)

    def bucket_fill(self, point, colour):
        """
        Paint a shape or a zone of the canvas with an arbitrary colour

        Args:
            point: the point from which to paint the connected shape or zone
            colour: the colour to paint with
        """
        if self._point_is_out_of_bound(point):
            raise OutOfCanvasBoundError()
        self._save_state()
        self._bucket_fill(point, colour)

    def _bucket_fill(self, point, colour, reset_content_type=False):
        content_type_to_fill, _ = self.cells[point.x][point.y]
        processed = set()
        to_process = [point]

        def can_process_cell(cell):
            #pylint: disable=missing-docstring
            return (cell not in processed and
                    cell not in to_process and
                    not self._point_is_out_of_bound(cell))

        while to_process != []:
            current_point = to_process.pop()
            processed.add(current_point)

            current_point_type, _ = self.cells[current_point.x][current_point.y]
            if current_point_type == content_type_to_fill:
                if reset_content_type:
                    self.cells[current_point.x][current_point.y] = (CanvasCellContentType.Empty, colour)
                else:
                    self.cells[current_point.x][current_point.y] = (content_type_to_fill, colour)
                #enqueue non processed neighbours
                left_neighbour = Point(current_point.x - 1, current_point.y)
                if can_process_cell(left_neighbour):
                    to_process.insert(0, left_neighbour)
                right_neighbour = Point(current_point.x + 1, current_point.y)
                if can_process_cell(right_neighbour):
                    to_process.insert(0, right_neighbour)
                top_neighbour = Point(current_point.x, current_point.y - 1)
                if can_process_cell(top_neighbour):
                    to_process.insert(0, top_neighbour)
                bottom_neighbour = Point(current_point.x, current_point.y + 1)
                if can_process_cell(bottom_neighbour):
                    to_process.insert(0, bottom_neighbour)

    def delete(self, point):
        """
        Delete a shape or reset the colour of a zone
        """
        if self._point_is_out_of_bound(point):
            raise OutOfCanvasBoundError()
        self._save_state()
        self._bucket_fill(point, ' ', reset_content_type=True)

    def undo(self):
        """
        Undo the last action
        """
        if self._previous_states != []:
            self.cells = self._previous_states.pop()

    def _save_state(self):
        self._previous_states.append(deepcopy(self.cells))

    def __str__(self):
        #pylint: disable=invalid-name
        canvas_str = ' ' + '-' * self.width + ' \n'
        for y in range(self.height):
            canvas_str += '|'
            for x in range(self.width):
                _, colour = self.cells[x][y]
                canvas_str += colour
            canvas_str += '|' + '\n'
        canvas_str += ' ' + '-' * self.width + ' '
        return canvas_str


class CanvasCellContentType(Enum):
    """
    The represent the possible content types of a canvas cell
    """
    Empty = 1
    Line = 2


class OutOfCanvasBoundError(Exception):
    #pylint: disable=missing-docstring
    pass


class Point(object):
    #pylint: disable=too-few-public-methods
    """
    Represents a point of the canvas

    Args:
        x, y: the integer coordinates of the point
    """
    def __init__(self, x, y):
        #pylint: disable=invalid-name
        self.x = int(x)
        self.y = int(y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(self.x * 97 + self.y * 101)


class Line(object):
    #pylint: disable=too-few-public-methods
    """
    Represents a line

    Args:
        from_point, to_point: the 2 points delimiting the line
    """
    def __init__(self, from_point, to_point):
        self.from_point = from_point
        self.to_point = to_point

    def __eq__(self, other):
        return self.from_point == other.from_point and self.to_point == other.to_point

    def get_points(self):
        """
            Returns the list of the points that are part of the line
        """
        if self._is_horizontal():
            return [Point(self.from_point.x, y) for y in range(self.from_point.y, self.to_point.y + 1)]
        elif self._is_vertical():
            return [Point(x, self.from_point.y) for x in range(self.from_point.x, self.to_point.x + 1)]
        else:
            raise NotImplementedError("Only horizontal and vertical lines are implemented so far")

    def _is_horizontal(self):
        return self.from_point.x == self.to_point.x

    def _is_vertical(self):
        return self.from_point.y == self.to_point.y


class Rectangle(object):
    #pylint: disable=too-few-public-methods
    """
    Represents a rectangle

    Args:
        top_left_point: the top-left corner of the rectangle
        bottom_right_point: the bottom-right corner of the rectangle
    """
    def __init__(self, top_left_point, bottom_right_point):
        self.top_left_point = top_left_point
        self.bottom_right_point = bottom_right_point

    def __eq__(self, other):
        return self.top_left_point == other.top_left_point \
           and self.bottom_right_point == other.bottom_right_point

    def get_lines(self):
        """
        Returns the 4 lines forming the rectangle
        """
        top_right_point = Point(self.bottom_right_point.x, self.top_left_point.y)
        bottom_left_point = Point(self.top_left_point.x, self.bottom_right_point.y)
        return [
            Line(self.top_left_point, top_right_point),
            Line(self.top_left_point, bottom_left_point),
            Line(top_right_point, self.bottom_right_point),
            Line(bottom_left_point, self.bottom_right_point)
        ]
