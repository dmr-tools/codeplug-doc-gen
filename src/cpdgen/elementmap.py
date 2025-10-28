from svgwrite import Drawing
from svgwrite.text import Text
from svgwrite.path import Path
from svgwrite.shapes import Rect
from cpdgen.pattern import ElementPattern, Address, Size
from xml.etree import ElementTree


class ElementMap:
    def __init__(self):
        self._margin_left, self._margin_top, self._margin_right, self._magin_bottom = 60, 30, 10, 10
        self._block_width, self._block_height = 40, 40
        self._border_radius, self._stroke_width = 5, 1
        self._document: Drawing = None

    @staticmethod
    def compute_compressed_bits(el: ElementPattern):
        compressed_bits = 0
        line_addresses = []
        for item in el:
            bits = item.get_size().bits()
            offset = item.get_address().bits()
            short = (bits <= 4)
            is_start = True
            while bits:
                bx, by = offset % 32, offset // 32
                is_end = ((bx+bits) <= 32)
                consume = bits if is_end else 32-bx
                if is_start or is_end:
                    compressed_bits += consume
                    if 0 == bx:
                        line_addresses.append(offset//8)
                bits -= consume
                offset += consume
                is_start = False
        return compressed_bits, line_addresses

    def process(self, el: ElementPattern):
        total_bits, line_addresses = ElementMap.compute_compressed_bits(el)
        total_rows = total_bits//32 + (1 if total_bits % 32 else 0)
        total_width = self._margin_left + self._margin_right + 32 * self._block_width
        total_height = self._margin_top + self._magin_bottom + total_rows * self._block_height
        self._document = Drawing(size=(total_width, total_height))

        for i in range(32):
            bit = 7 - i % 8
            x, y = self._margin_left + i*self._block_width, 0
            w, h = self._block_width, self._margin_top
            label = Text(str(bit), x=(x+w//2,), y=(y+h//2,), text_anchor="middle")
            self._document.add(label)

        for i in range(total_rows):
            address = line_addresses[i]
            x, y = 0, self._margin_top + i*self._block_height
            w, h = self._margin_left, self._block_height
            label = Text("{:04x}".format(address), x=(x+5,), y=(y+h//2,), dominant_baseline="middle")
            self._document.add(label)

        compressed_offset = 0
        for item in el:
            bits = item.get_size().bits()
            offset = item.get_address().bits()
            short = (bits <= 4)
            is_start = True
            while bits:
                bx, by = offset % 32, offset // 32
                cx, cy = compressed_offset % 32, compressed_offset // 32
                is_end = ((bx+bits) <= 32)
                consume = bits if is_end else 32-bx
                if is_start or is_end:
                    name = item.meta().get_short_name() if short and item.meta().has_short_name() else item.meta().get_name()
                    self.draw_block(name, cx, cy, consume, is_start, is_end)
                    compressed_offset += consume
                bits -= consume
                offset += consume
                is_start = False


    def draw_block(self, name, bx, by, length, is_start, is_end):
        x, y = self._margin_left + bx*self._block_width, self._margin_top + by*self._block_height
        width, height = length*self._block_width, self._block_height
        r, sw = self._border_radius, self._stroke_width
        spath = Path(stroke="#000000", stroke_width=sw, fill="none")
        fpath = Path(stroke="none", stroke_width=0, fill="#eeeeee")
        spath.push("M{},{} ".format(x+r, y+height-sw))
        fpath.push("M{},{} ".format(x+r, y+height-sw))
        if is_start:
            spath.push_arc((x, y+height-r-sw), 0, r, False, "+", True)
            spath.push("L{},{}".format(x, y+r+sw))
            spath.push_arc((x+r, y+sw), 0, r, False, "+", True)
            fpath.push_arc((x, y+height-r-sw), 0, r, False, "+", True)
            fpath.push("L{},{}".format(x, y+r+sw))
            fpath.push_arc((x+r, y+sw), 0, r, False, "+", True)
        else:
            spath.push("L{},{} M{},{} L{},{}".format(x, y+height-sw, x, y+sw, x+r, y+sw))
            fpath.push("L{},{} L{},{} L{},{}".format(x, y+height-sw, x, y+sw, x+r, y+sw))
        spath.push("L{},{}".format(x+width-r, y+sw))
        fpath.push("L{},{}".format(x+width-r, y+sw))
        if is_end:
            spath.push_arc((x+width, y+r+sw), 0, r, False, "+", True)
            spath.push("L{},{}".format(x+width, y+height-r-sw))
            spath.push_arc((x+width-r, y+height-sw), 0, r, False, "+", True)
            fpath.push_arc((x+width, y+r+sw), 0, r, False, "+", True)
            fpath.push("L{},{}".format(x+width, y+height-r-sw))
            fpath.push_arc((x+width-r, y+height-sw), 0, r, False, "+", True)
        else:
            spath.push("L{},{} M{},{} L{},{}".format(x+width, y+sw, x+width, y+height-sw, x+width-r, y+height-sw))
            fpath.push("L{},{} L{},{} L{},{}".format(x+width, y+sw, x+width, y+height-sw, x+width-r, y+height-sw))
        spath.push("L{},{}".format(x+r, y+height-sw))
        fpath.push("L{},{}".format(x+r, y+height-sw))
        self._document.add(fpath)
        self._document.add(spath)
        if is_start:
            text = Text(name, x=(x+r,), y=(y+height/2+sw,), dominant_baseline="middle", font_size="12pt")
        else:
            text = Text("...", x=(x+width/2,), y=(y+height/2+sw,), text_anchor="middle", font_size="12pt")
        self._document.add(text)

    def xml(self) -> ElementTree:
        return self._document.get_xml()

    def document(self) -> Drawing:
        return self._document
