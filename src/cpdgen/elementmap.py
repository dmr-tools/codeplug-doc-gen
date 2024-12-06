from svgwrite import Drawing
from svgwrite.text import Text
from svgwrite.path import Path
from cpdgen.pattern import ElementPattern, Address, Size
from xml.etree import ElementTree

class ElementMap:
    def __init__(self, drawing: Drawing):
        self._margin_left, self._margin_top, self._margin_right, self._magin_bottom = 10, 10, 10, 10
        self._block_width, self._block_height = 30, 30
        self._border_radius, self._stroke_width = 5, 1
        self._document: Drawing = drawing

    def process(self, el: ElementPattern):
        for item in el:
            bits = item.get_size().bits()
            offset = item.get_address().bits()
            is_start = True
            while bits:
                bx, by = offset % 32, offset // 32
                is_end = ((bx+bits) <= 32)
                consume = bits if is_end else 32-bx
                self.draw_block(item.meta().get_name(), bx, by, consume, is_start, is_end)
                bits -= consume
                is_start = False

    def draw_block(self, name, bx, by, length, is_start, is_end):
        x, y = self._margin_left + bx*self._block_width, self._margin_top + by*self._block_height
        width, height = length*self._block_width, self._block_height
        r, sw = self._border_radius, self._stroke_width
        path = Path(stroke="#000000", fill="#eeeeee", stroke_width=sw)
        path.push("M{},{} ".format(x+r, y+height-sw))
        if is_start:
            path.push_arc((x, y+height-r-sw), 0, r, False, "+", True)
            path.push("L{},{}".format(x, y+r+sw))
            path.push_arc((x+r, y+sw), 0, r, False, "+", True)
        else:
            path.push("L{},{}".format(x, y+height-sw))
            path.push("M{},{}".format(x, y+sw))
            path.push("L{},{}".format(x+r, y+sw))
        path.push("L{},{}".format(x+width-r, y+sw))
        if is_end:
            path.push_arc((x+width, y+r+sw), 0, r, False, "+", True)
            path.push("L{},{}".format(x+width, y+height-r-sw))
            path.push_arc((x+width-r, y+height-sw), 0, r, False, "+", True)
        else:
            path.push("L{},{}".format(x+width, y+sw))
            path.push("M{},{}".format(x+width, y+height-sw))
            path.push("L{},{}".format(x+width-r, y+height-sw))
        path.push("L{},{}".format(x+r,y+height-sw))
        path.push("z")
        self._document.add(path)
        if is_start:
            text = Text(name, x=(x+r,), y=(y+height/2+sw,))
        else:
            text = Text("...", x=(x+width/2,), y=(y+height/2+sw,))
        self._document.add(text)

    def xml(self) -> ElementTree:
        return self._document.get_xml()

    def document(self) -> Drawing:
        return self._document
