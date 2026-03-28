from typing import Union

from cpdgen.document import Document, DocumentSegment, Paragraph, Section
from cpdgen.pattern import *


class DifferenceGenerator:
    def __init__(self):
        self._documents: list[Document] = []
        self._stack: list[DocumentSegment|Document] = []

    def documents(self):
        return self._documents

    def push(self, segment: Document|DocumentSegment):
        self._stack.append(segment)

    def back(self) -> DocumentSegment|Document:
        return self._stack[-1]

    def pop(self):
        return self._stack.pop()

    def document(self):
        for el in reversed(self._stack):
            if isinstance(el, Document):
                return el
        return None

    def process(self, orig:Codeplug, dest:Codeplug):
        assert isinstance(orig, Codeplug) and isinstance(dest, Codeplug)
        self._documents = [Document()]
        self._stack = [self._documents[-1]]
        self._compare_children(orig, dest)

    def _compare_children(self, orig:ElementPattern|Codeplug, dest:ElementPattern|Codeplug):
        difference: bool = False
        i,j = 0,0
        while i<len(orig) or j<len(dest):
            if i == len(orig):
                difference |= self._insert(dest[j])
                j += 1
                continue
            if j == len(dest):
                difference |= self._delete(orig[i])
                i += 1
                continue
            # Not at end
            left, right = orig[i], dest[j]
            if left.get_address() < right.get_address():
                difference |= self._delete(left); i += 1
            elif left.get_address() > right.get_address():
                difference |= self._insert(right); j += 1
            elif type(left) != type(right):
                difference |= self._replace(left, right)
                i += 1; j += 1
            else:
                difference |= self._compare(left, right)
                i += 1; j += 1
        return difference

    def _delete(self, left:AbstractPattern):
        if isinstance(left, FieldPattern):
            p = Paragraph(title=f"Remove {left.meta().get_name()}")
            self.back().add(p)
        else:
            sec = Section(title=f"Remove {left.meta().get_name()}")
            self.back().add(sec)
            p = Paragraph(); sec.add(p)
        if left.has_address():
            p.add(f"Remove element at address {left.get_address()}.")
        return True

    def _insert(self, right:AbstractPattern):
        if isinstance(right, FieldPattern):
            p = Paragraph(title=f"Insert {right.meta().get_name()}")
            self.back().add(p)
        else:
            sec = Section(title=f"Insert {right.meta().get_name()}")
            self.back().add(sec)
            p = Paragraph(); sec.add(p)
        if right.has_address():
            p.add(f"Insert element at address {right.get_address()}.")
        return True

    def _replace(self, left:AbstractPattern, right:AbstractPattern):
        if isinstance(right, FieldPattern):
            p = Paragraph(title=f"Replace {left.meta().get_name()} with {right.meta().get_name()}")
            self.back().add(p)
        else:
            sec = Section(title=f"Replace {left.meta().get_name()} with {right.meta().get_name()}")
            self.back().add(sec)
            p = Paragraph(); sec.add(p)
        if isinstance(left, FixedPattern) and isinstance(right, FixedPattern) and left.get_size() != right.get_size():
            p.add(f"Replace element at address {left.get_address()} "
                  f"of size {left.get_size()} with one of size {right.get_size()}.");
        else:
            p.add(f"Replace elements at address {left.get_address()}.")
        return True

    def _compare(self, left:AbstractPattern, right:AbstractPattern):
        assert type(left) == type(right)
        assert left.get_address() == right.get_address()
        difference = False
        if isinstance(left, SparseRepeat):
            difference |= self._compare_sparse_repeat(left, right)
        elif isinstance(left, BlockRepeat):
            difference |= self._compare_block_repeat(left, right)
        elif isinstance(left, FixedRepeat):
            difference |= self._compare_fixed_repeat(left, right)
        elif isinstance(left, UnionPattern):
            difference |= self._compare_union(left, right)
        elif isinstance(left, ElementPattern):
            difference |= self._compare_element(left, right)
        elif isinstance(left, FieldPattern):
            difference |= self._compare_field(left, right)
        return difference

    def _compare_field(self, left:FieldPattern, right:FieldPattern):
        difference = False
        if isinstance(left, EnumPattern):
            difference |= self._compare_enum(left, right)
        elif isinstance(left, IntegerPattern):
            difference |= self._compare_integer(left, right)
        elif isinstance(left, StringPattern):
            difference |= self._compare_string(left, right)
        elif isinstance(left, (UnusedDataPattern|UnknownDataPattern)):
            difference |= self._compare_unknown(left, right)
        return difference

    def _compare_sparse_repeat(self, left:SparseRepeat, right:SparseRepeat):
        sec = Section(title=f"In sparse repeat {left.meta().get_name()}")
        self.push(sec)
        difference = False
        if left.meta().get_name() != right.meta().get_name():
            p = Paragraph()
            p.add(f"Replace name {left.meta().get_name()} with {right.meta().get_name()}.")
            sec.add(p)
            difference = True
        if left.get_min() != right.get_min():
            p = Paragraph()
            p.add(f"Replace min {left.get_min()} with {right.get_min()}.")
            sec.add(p)
            difference = True
        if left.get_max() != right.get_max():
            p = Paragraph()
            p.add(f"Replace max {left.get_max()} with {right.get_max()}.")
            sec.add(p)
            difference = True
        if left.get_offset() != right.get_offset():
            p = Paragraph()
            p.add(f"Replace offset {left.get_offset()} with {right.get_offset()}.")
            sec.add(p)
            difference = True
        difference |= self._compare(left.get_child(), right.get_child())
        self.pop()
        if difference: self.back().add(sec)
        return difference

    def _compare_block_repeat(self, left:BlockRepeat, right:BlockRepeat):
        sec = Section(title=f"In block repeat {left.meta().get_name()}")
        self.push(sec)
        difference = False
        if left.meta().get_name() != right.meta().get_name():
            p = Paragraph()
            p.add(f"Replace name {left.meta().get_name()} with {right.meta().get_name()}.")
            sec.add(p)
            difference = True
        if left.get_min() != right.get_min():
            p = Paragraph()
            p.add(f"Replace min {left.get_min()} with {right.get_min()}.")
            sec.add(p)
            difference = True
        if left.get_max() != right.get_max():
            p = Paragraph()
            p.add(f"Replace max {left.get_max()} with {right.get_max()}.")
            sec.add(p)
            difference = True
        difference |= self._compare(left.get_child(), right.get_child())
        self.pop()
        if difference: self.back().add(sec)
        return difference

    def _compare_fixed_repeat(self, left:FixedRepeat, right:FixedRepeat):
        sec = Section(title=f"In fixed repeat {left.meta().get_name()}")
        self.push(sec)
        difference = False
        if left.meta().get_name() != right.meta().get_name():
            p = Paragraph()
            p.add(f"Replace name {left.meta().get_name()} with {right.meta().get_name()}.")
            sec.add(p)
            difference = True
        if left.get_size() != right.get_size():
            p = Paragraph()
            p.add(f"Replace size {left.get_size()} with {right.get_size()}.")
            sec.add(p)
            difference = True
        difference |= self._compare(left.get_child(), right.get_child())
        self.pop()
        if difference: self.back().add(sec)
        return difference

    def _compare_union(self, left:Union, right:Union):
        sec = Section(title=f"In union {left.meta().get_name()}")
        self.push(sec)
        difference = False
        if left.meta().get_name() != right.meta().get_name():
            p = Paragraph()
            p.add(f"Replace name {left.meta().get_name()} with {right.meta().get_name()}.")
            sec.add(p)
            difference = True
        i, j = 0,0
        while i < len(left) or j < len(right):
            if i == len(left):
                difference |= self._insert(right[j])
                j += 1
                continue
            if j == len(right):
                difference |= self._delete(left[i])
                i += 1
                continue
            difference |= self._compare(left[i], right[j])
            i += 1; j+=1
        self.pop()
        if difference: self.back().add(sec)
        return difference

    def _compare_element(self, left:ElementPattern, right:ElementPattern):
        sec = Section(title=f"In element {left.meta().get_name()}")
        self.push(sec)
        difference = False
        if left.meta().get_name() != right.meta().get_name():
            p = Paragraph()
            p.add(f"Replace name {left.meta().get_name()} with {right.meta().get_name()}.")
            sec.add(p)
            difference = True
        difference |= self._compare_children(left, right)
        self.pop()
        if difference: self.back().add(sec)
        return difference

    def _compare_enum(self, left:EnumPattern, right:EnumPattern):
        p = Paragraph(f"In enum {left.meta().get_name()}")
        p.add(f"At address {left.get_address()}")
        difference = False
        if left.meta().get_name() != right.meta().get_name():
            p.add(f"Replace name {left.meta().get_name()} with {right.meta().get_name()}.")
            difference = True
        if left.get_size() != right.get_size():
            p.add(f"Change size from {left.get_size()} to {right.get_size()}.")
            difference |= True
        if left.has_default_value() and not right.has_default_value():
            p.add(f"Remove default value {left.get_default_value()}.")
        elif right.has_default_value() and not left.has_default_value():
            p.add(f"Add default value {right.get_default_value()}.")
        elif left.has_default_value() and left.get_default_value() != right.get_default_value():
            p.add(f"Replace default {left.get_default_value()} with {right.get_default_value()}.")
            difference |= True
        i,j = 0,0
        while i < len(left) or j < len(right):
            if i == len(left):
                p.add(f"Add item {right[j].get_name()} with value {right[j].value}.")
                difference |= True
                j += 1
                continue
            if j == len(right):
                p.add(f"Remove item {left[i].get_name()} with value {left[i].value}.")
                difference |= True
                i += 1
                continue
            if left[i].value != right[j].value:
                p.add(f"Replace item {left[i].get_name()} (value {left[i].value}) with {right[j].get_name()} (value {right[j].value}).")
            i += 1; j+=1
        if difference: self.back().add(p)
        return difference

    def _compare_integer(self, left:IntegerPattern, right:IntegerPattern):
        p = Paragraph(f"In integer {left.meta().get_name()}")
        p.add(f"At address {left.get_address()}")
        difference = False
        if left.meta().get_name() != right.meta().get_name():
            p.add(f"Replace name {left.meta().get_name()} with {right.meta().get_name()}.")
            difference = True
        if left.get_size() != right.get_size():
            p.add(f"Change size from {left.get_size()} to {right.get_size()}.")
            difference |= True
        if left.has_default_value() and not right.has_default_value():
            p.add(f"Remove default value {left.get_default_value()}.")
        elif right.has_default_value() and not left.has_default_value():
            p.add(f"Add default value {right.get_default_value()}.")
        elif left.has_default_value() and left.get_default_value() != right.get_default_value():
            p.add(f"Replace default {left.get_default_value()} with {right.get_default_value()}.")
            difference |= True
        if left.has_range() and not right.has_range():
            p.add(f"Remove range {left.get_range()}.")
            difference |= True
        elif right.has_range() and not left.has_range():
            p.add(f"Add range {right.get_range()}.")
            difference |= True
        if difference: self.back().add(p)
        return difference

    def _compare_string(self, left:StringPattern, right:StringPattern):
        p = Paragraph(f"In string {left.meta().get_name()}")
        p.add(f"At address {left.get_address}")
        difference = False
        if left.meta().get_name() != right.meta().get_name():
            p.add(f"Replace name {left.meta().get_name()} with {right.meta().get_name()}.")
            difference = True
        if left.get_size() != right.get_size():
            p.add(f"Change size from {left.get_size()} to {right.get_size()}.")
            difference |= True
        if difference: self.back().add(p)
        return difference


    def _compare_unknown(self, left:UnknownDataPattern|UnusedDataPattern, right:UnknownDataPattern|UnusedDataPattern):
        p = Paragraph(f"In unknown/unused data {left.meta().get_name()}")
        p.add(f"At address {left.get_address()}")
        difference = False
        if left.get_size() != right.get_size():
            p.add(f"Change size from {left.get_size()} to {right.get_size()}.")
            difference |= True
        if difference: self.back().add(p)
        return difference
