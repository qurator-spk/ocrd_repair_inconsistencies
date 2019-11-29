from __future__ import absolute_import

import os.path
from collections import Sequence

from ocrd import Processor
from ocrd_modelfactory import page_from_file
from ocrd_models.ocrd_page import (
    TextRegionType, TextLineType, WordType,
    MetadataItemType, LabelsType, LabelType,
    to_xml
)
from ocrd_utils import (
    getLogger, concat_padded,
    polygon_from_points,
    MIMETYPE_PAGE
)
from shapely.geometry import Polygon

from .config import OCRD_TOOL

TOOL = 'ocrd-repair-inconsistencies'
LOG = getLogger('processor.RepairInconsistencies')


class RepairInconsistencies(Processor):

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = OCRD_TOOL['tools'][TOOL]
        super(RepairInconsistencies, self).__init__(*args, **kwargs)

    def process(self):
        for (n, input_file) in enumerate(self.input_files):
            page_id = input_file.pageId or input_file.ID
            LOG.info("INPUT FILE %i / %s", n, page_id)
            pcgts = page_from_file(self.workspace.download_file(input_file))
            page = pcgts.get_Page()
            
            # add metadata about this operation and its runtime parameters:
            metadata = pcgts.get_Metadata() # ensured by from_file()
            metadata.add_MetadataItem(
                MetadataItemType(type_="processingStep",
                                 name=self.ocrd_tool['steps'][0],
                                 value=TOOL,
                                 Labels=[LabelsType(
                                     externalModel="ocrd-tool",
                                     externalId="parameters",
                                     Label=[LabelType(type_=name,
                                                      value=self.parameter[name])
                                            for name in self.parameter.keys()])]))
            
            regions = page.get_TextRegion()

            for region in regions:
                textLineOrder = 'top-to-bottom'
                for segment in [region, page]:
                    if segment.textLineOrder is None:
                        continue
                    else:
                        textLineOrder = segment.textLineOrder
                        break
                if textLineOrder not in ['top-to-bottom', 'bottom-to-top']:
                    LOG.info('Not processing page "%s" region "%s" (textLineOrder=%s)',
                             page_id, region.id, textLineOrder)
                    continue

                _fix_segment(region, page_id, reverse=textLineOrder=='bottom-to-top')

                lines = region.get_TextLine()
                for line in lines:
                    readingDirection = 'left-to-right'
                    for segment in [line, region, page]:
                        if segment.readingDirection is None:
                            continue
                        else:
                            readingDirection = segment.readingDirection
                            break
                    if readingDirection not in ['left-to-right', 'right-to-left']:
                        LOG.info('Not processing page "%s" line "%s" (readingDirection=%s)',
                                 page_id, line.id, readingDirection)
                        continue
                    
                    _fix_segment(line, page_id, reverse=readingDirection=='right-to-left')

                    words = line.get_Word()
                    for word in words:
                        readingDirection = 'left-to-right'
                        for segment in [word, line, region, page]:
                            if segment.readingDirection is None:
                                continue
                            else:
                                readingDirection = segment.readingDirection
                                break
                        if readingDirection not in ['left-to-right', 'right-to-left']:
                            LOG.info('Not processing page "%s" word "%s" (readingDirection=%s)',
                                     page_id, word.id, readingDirection)
                            continue

                        _fix_segment(word, page_id, reverse=readingDirection=='right-to-left')

            file_id = input_file.ID.replace(self.input_file_grp, self.output_file_grp)
            if file_id == input_file.ID:
                file_id = concat_padded(self.output_file_grp, n)
            self.workspace.add_file(
                ID=file_id,
                file_grp=self.output_file_grp,
                pageId=input_file.pageId,
                mimetype=MIMETYPE_PAGE,
                local_filename=os.path.join(self.output_file_grp, file_id + '.xml'),
                content=to_xml(pcgts))


def get_text(thing, joiner=''):
    """Get the text of the given thing, joining if necessary"""

    def _get_text_for_one(one):
        try:
            return one.get_TextEquiv()[0].get_Unicode()
        except Exception:
            LOG.warning('element "%s" has no text', one.id)
            return None
    
    if isinstance(thing, Sequence):
        texts = [_get_text_for_one(part) for part in thing]
        if all(texts):
            return joiner.join(texts)
        else:
            return None
    else:
        return _get_text_for_one(thing)

def _fix_segment(segment, page_id, reverse=False):
    """Fix order of child elements of (region/line/word) segment."""
    
    if isinstance(segment, TextRegionType):
        joiner = '\n'
        sort_horizontal = False
        children = segment.get_TextLine()
        adoption = segment.set_TextLine
    elif isinstance(segment, TextLineType):
        joiner = ' '
        sort_horizontal = True
        children = segment.get_Word()
        adoption = segment.set_Word
    elif isinstance(segment, WordType):
        joiner = ''
        sort_horizontal = True
        children = segment.get_Glyph()
        adoption = segment.set_Glyph
    else:
        raise Exception('invalid element type %s of segment to fix' % type(segment))
    if not children:
        return
    segment_text = get_text(segment)
    concat_text = get_text(children, joiner)
    if (segment_text and concat_text and
        segment_text != concat_text and
        segment_text.replace(joiner, '') != concat_text.replace(joiner, '')):
        def polygon_position(child, horizontal=sort_horizontal):
            polygon = Polygon(polygon_from_points(child.get_Coords().points))
            if horizontal:
                return polygon.centroid.x
            else:
                return polygon.centroid.y
        sorted_children = sorted(children, reverse=reverse, key=polygon_position)
        sorted_concat_text = get_text(sorted_children, joiner)
        
        if (segment_text == sorted_concat_text or
            segment_text.replace(joiner, '') == sorted_concat_text.replace(joiner, '')):
            LOG.info('Fixing element order of page "%s" segment "%s"', page_id, segment.id)
            adoption(sorted_children)
        else:
            LOG.debug('Resorting children of page "%s" segment "%s" from %s to %s does not suffice to turn "%s" into "%s"',
                      page_id, segment.id,
                      str([seg.id for seg in children]),
                      str([seg.id for seg in sorted_children]),
                      concat_text, segment_text)
