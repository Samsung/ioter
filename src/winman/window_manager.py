from winman.guider import Guider
from common.utils import singleton

DEBUG = False


class Position():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self, r2):
        # Tests if another rectangle is contained by this one
        return (r2.y >= self.y and
                r2.x >= self.x and
                r2.y + r2.h <= self.y + self.h and
                r2.x + r2.w <= self.x + self.w)

    def overlapped(self, r2):
        if (self.x == r2.x and self.w == r2.w):
            if self.y > r2.y:
                return r2.y + r2.h >= self.y
            else:
                return self.y + self.h >= r2.y
        elif (self.y == r2.y and self.h == r2.h):
            if self.x > r2.x:
                return r2.x + r2.w >= self.x
            else:
                return self.x + self.w >= r2.x

    def intersects(self, r2):
        # Find intersects
        return not (self.x + self.w <= r2.x or
                    self.x >= r2.x + r2.w or
                    self.y + self.h <= r2.y or
                    self.y >= r2.y + r2.h)

    def __str__(s):
        return "Position ({0}, {1}, {2}, {3})".format(s.x, s.y, s.w, s.h)


@singleton
class WindowManager():

    def __init__(self, *args, **kwargs):
        self.screen_width = args[2]
        self.screen_height = args[3]
        self.cur_pos_x = 761
        self.cur_pos_y = 288
        self.title_bar_height = 37

        p = Position(args[0], args[1], self.screen_width, self.screen_height)
        self.free_rectangles = [p]
        self.used_positions = []
        print("WindowManager init(): Screen", self.free_rectangles[0])

    def getCenterPosition(self):
        x = self.cur_pos_x
        y = self.cur_pos_y
        self.cur_pos_x += self.title_bar_height + 1
        self.cur_pos_y += self.title_bar_height + 1
        return x, y

    def joinRectangles(self, rectangles):
        # Make combinations and compare them
        sub_rectangles = []
        join_rectangles = []
        for i in range(len(rectangles)):
            for j in range(i + 1, len(rectangles)):
                if rectangles[i].contains(rectangles[j]):
                    sub_rectangles.append(rectangles[j])
                elif rectangles[j].contains(rectangles[i]):
                    sub_rectangles.append(rectangles[i])
                elif self.overlapped(rectangles[i], rectangles[j]):
                    join_rectangle = self.join(rectangles[i], rectangles[j])
                    join_rectangles.append(join_rectangle)
                    sub_rectangles.append(rectangles[i])
                    sub_rectangles.append(rectangles[j])
        new_rectangles = set(rectangles) - set(sub_rectangles)
        new_rectangles.update(set(join_rectangles))
        return list(new_rectangles)

    def addWithPosition(self, x, y, width, height):
        p = Position(x, y, width, height)
        if DEBUG is True:
            print("addWithPosition(): ", p)
        self.used_positions.append(p)
        prev_rectangles = []
        subtract_rectangles = []

        for free_rectangle in self.free_rectangles:
            # Find an intersection between free rectangle and selected rectangle
            if free_rectangle.intersects(p):
                # Subtract selected rectangle from free rectangle
                subtract_rectangles.extend(
                    self.subtract_rectangle(free_rectangle, p))
            else:
                prev_rectangles.append(free_rectangle)
        # Join rectangles to reduce number
        new_free_rectangles = prev_rectangles + subtract_rectangles
        self.free_rectangles = self.joinRectangles(new_free_rectangles)

        return x, y

    def add(self, width, height):
        # Find a best position to put rectangle
        selected = self.find_position(self.free_rectangles, width, height)
        if DEBUG is True:
            print("add(): ", selected)
        # Failed to find (No room for rectagle)
        if selected.x == -1:
            return self.getCenterPosition()
        p = Position(selected.x, selected.y, width, height)

        return self.addWithPosition(selected.x, selected.y, width, height)

    def remove(self, x, y, width, height):
        p = Position(x, y, width, height)
        if DEBUG is True:
            print("remove()", p)
        for item in self.used_positions:
            if p.x == item.x and p.y == item.y and p.w == item.w and p.h == item.h:
                if DEBUG is True:
                    print("removed", item)
                self.used_positions.remove(item)
                self.free_rectangles.append(item)
                self.free_rectangles = self.joinRectangles(
                    self.free_rectangles)

                return True
        return False

    def dumpRectangles(self):
        print("==DUMP=========")
        print("Free rectangles")
        i = 1
        for item in self.free_rectangles:
            print(i, item)
            i += 1
        print("===============")

        print("Used rectangles")
        i = 1
        for item in self.used_positions:
            print(i, item)
            i += 1
        print("==========END==")

    def join(self, r1, r2):
        assert self.overlapped(r1, r2)

        r1.right = r1.x + r1.w
        r1.bottom = r1.y + r1.h
        r2.right = r2.x + r2.w
        r2.bottom = r2.y + r2.h
        res = Position(r1.x, r1.y, r1.w, r1.h)

        # Two rectangles are overlapped from up and down
        if r1.x == r2.x and r1.w == r2.w:
            y_min = min(r1.y, r2.y)
            y_max = max(r1.bottom, r2.bottom)
            res.y = y_min
            res.h = y_max - y_min
        # Two rectangles are overlapped from left and right
        elif r1.y == r2.y and r1.h == r2.h:
            x_min = min(r1.x, r2.x)
            x_max = max(r1.right, r2.right)
            res.x = x_min
            res.w = x_max - x_min
        return res

    def overlapped(self, r1, r2):
        if r1.x == r2.x and r1.w == r2.w:
            if r1.y > r2.y:
                return r2.y + r2.h >= r1.y
            else:
                return r1.y + r1.h >= r2.y
        elif r1.y == r2.y and r1.h == r2.h:
            if r1.x > r2.x:
                return r2.x + r2.w >= r1.x
            else:
                return r1.x + r1.w >= r2.x

    def find_position(self, free_rectangles, width, height):
        best_height = float('inf')
        best_rectangle = Position(-1, -1, width, height)
        for rectangle in free_rectangles:
            # If rectangle size is smaller than or equals to empty area
            if rectangle.w >= width and rectangle.h >= height:
                # Height order - If there are more than one to place, select it which is the height is smaller
                if rectangle.h < best_height:
                    best_height = rectangle.h
                    best_rectangle = rectangle
        return best_rectangle

    def subtract_rectangle(self, s, r):
        # NOTE: s(free_rectangle) is always larger than r
        ret = []
        # Left
        if r.x > s.x:
            ret.append(Position(s.x, s.y, r.x - s.x, s.h))
        # Right
        if r.x + r.w < s.x + s.w:
            ret.append(Position(r.x + r.w, s.y, s.x + s.w - (r.x + r.w), s.h))
        # Top
        if r.y > s.y:
            ret.append(Position(s.x, s.y, s.w, r.y - s.y))
        # Bottom
        if r.y + r.h < s.y + s.h:
            ret.append(Position(s.x, r.y + r.h, s.w, s.y + s.h - (r.y + r.h)))
        return ret

    def showGuide(self):
        self.g = Guider(self.free_rectangles)
        self.g.showFullScreen()

    def maximal_rectangles(self, bin_width, bin_height, rectangles):
        # Empty area (in rectangle shape)
        free_rectangles = [Position(0, 0, bin_width, bin_height)]
        # Using area (in rectangle shape)
        used_rectangles = []
        for rectangle in rectangles:
            (width, height) = rectangle
            # Find a best position to put rectangle
            selected = self.find_position(free_rectangles, width, height)
            x = selected.x
            y = selected.y
            # Failed to find (No room for rectagle)
            if x == -1:
                return None
            used_rectangles.append((x, y, width, height))
            prev_rectangles = []
            subtract_rectangles = []
            for free_rectangle in free_rectangles:
                # Find an intersection between free rectangle and selected rectangle
                if free_rectangle.intersects(Position(x, y, width, height)):
                    # Subtract selected rectangle from free rectangle
                    subtract_rectangles += self.subtract_rectangle(
                        free_rectangle, (x, y, width, height))
                else:
                    prev_rectangles.append(free_rectangle)
            # Join rectangles to reduce number
            new_free_rectangles = prev_rectangles + subtract_rectangles
            # Make combinations and compare them
            sub_rectangles = []
            for i in range(len(new_free_rectangles)):
                for j in range(i + 1, len(new_free_rectangles)):
                    if new_free_rectangles[i].contains(new_free_rectangles[j]):
                        sub_rectangles.append(new_free_rectangles[j])
                    if new_free_rectangles[j].contains(new_free_rectangles[i]):
                        sub_rectangles.append(new_free_rectangles[i])
            new_free_rectangles = set(
                new_free_rectangles) - set(sub_rectangles)
            free_rectangles = new_free_rectangles
        return used_rectangles
