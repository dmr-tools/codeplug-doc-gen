from cpdgen.document import Document, Section, Paragraph, Table, Figure


class Indexer:
    @staticmethod
    def process(obj, counts={'sections': [0], 'paragraphs': [0], 'tables': [0], 'figures': [0]}):
        if isinstance(obj, Document):
            for section in obj:
                Indexer.process(section)
        elif isinstance(obj, Section):
            counts['sections'][-1] += 1
            obj._number = counts['sections'][-1]
            obj.set_segment_id("sec" + ".".join(map(str, counts['sections'])))
            counts['sections'].append(0)
            for segment in obj:
                Indexer.process(segment)
            counts['sections'].pop()
        elif isinstance(obj, Paragraph):
            counts['paragraphs'][-1] += 1
            obj._number = counts['paragraphs'][-1]
            obj.set_segment_id("par" + ".".join(map(str, counts['sections'])))
            counts['paragraphs'].append(0)
        elif isinstance(obj, Table):
            counts['tables'][-1] += 1
            obj._number = counts['tables'][-1]
            obj.set_segment_id("tab" + ".".join(map(str, counts['sections'])))
            counts['tables'].append(0)
        elif isinstance(obj, Figure):
            counts['figures'][-1] += 1
            obj._number = counts['figures'][-1]
            obj.set_segment_id("fig" + ".".join(map(str, counts['sections'])))
            counts['figures'].append(0)

