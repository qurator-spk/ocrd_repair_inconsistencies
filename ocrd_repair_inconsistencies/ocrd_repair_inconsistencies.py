from __future__ import absolute_import

import os.path
from collections import Sequence

from ocrd import Processor
from ocrd_modelfactory import page_from_file
from ocrd_models.ocrd_page import (
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

                _fix_lines(region, page_id, reverse=textLineOrder=='bottom-to-top')

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
                    
                    _fix_words(line, page_id, reverse=readingDirection=='right-to-left')

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

                        _fix_glyphs(word, page_id, reverse=readingDirection=='right-to-left')

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


def get_text(thing, joiner=None):
    """Get the text of the given thing, joining if necessary"""

    def _get_text_for_one(t):
        if len(t.get_TextEquiv()) != 1:
            raise NotImplementedError
        try:
            return t.get_TextEquiv()[0].get_Unicode()
        except Exception:
            return None

    if isinstance(thing, Sequence):
        text = joiner.join(_get_text_for_one(t) for t in thing)
    else:
        text = _get_text_for_one(thing)
    return text


def _fix_words(line, page_id, reverse=False):
    """Fix word order in a line"""

    words = line.get_Word()
    if not words:
        return
    line_text = get_text(line)
    words_text = get_text(words, ' ')
    if line_text != words_text:
        sorted_words = sorted(words, reverse=reverse,
                              key=lambda w: Polygon(polygon_from_points(w.get_Coords().points)).centroid.x)
        sorted_words_text = get_text(sorted_words, ' ')

        if sorted_words_text == line_text:
            LOG.info('Fixing word order of page "%s" line "%s"', page_id, line.id)
            line.set_Word(sorted_words)
        else:
            LOG.debug('Resorting lines of page "%s" region "%s" from %s to %s does not suffice to turn "%s" into "%s"',
                      page_id, line.id,
                      str([word.id for word in words]),
                      str([word.id for word in sorted_words]),
                      words_text, line_text)


def _fix_glyphs(word, page_id, reverse=False):
    """Fix glyph order in a word"""

    glyphs = word.get_Glyph()
    if not glyphs:
        return
    word_text = get_text(word)
    glyphs_text = get_text(glyphs, '')
    if word_text != glyphs_text:
        sorted_glyphs = sorted(glyphs, reverse=reverse,
                               key=lambda g: Polygon(polygon_from_points(g.get_Coords().points)).centroid.x)
        sorted_glyphs_text = get_text(sorted_glyphs, '')

        if sorted_glyphs_text == word_text:
            LOG.info('Fixing glyph order of page "%s" word "%s"', page_id, word.id)
            word.set_Glyph(sorted_glyphs)
        else:
            LOG.debug('Resorting glyphs of page "%s" word "%s" from %s to %s does not suffice to turn "%s" into "%s"',
                      page_id, word.id,
                      str([glyph.id for glyph in glyphs]),
                      str([glyph.id for glyph in sorted_glyphs]),
                      glyphs_text, word_text)


def _fix_lines(region, page_id, reverse=False):
    """Fix line order in a region"""

    lines = region.get_TextLine()
    if not lines:
        return
    region_text = get_text(region)
    lines_text = get_text(lines, '\n')
    if region_text != lines_text:
        sorted_lines = sorted(lines, reverse=reverse,
                              key=lambda l: Polygon(polygon_from_points(l.get_Coords().points)).centroid.y)
        sorted_lines_text = get_text(sorted_lines, '\n')

        if sorted_lines_text == region_text:
            LOG.info('Fixing line order of page "%s" region "%s"', page_id, region.id)
            region.set_TextLine(sorted_lines)
        else:
            LOG.debug('Resorting lines of page "%s" region "%s" from %s to %s does not suffice to turn "%s" into "%s"',
                      page_id, region.id,
                      str([line.id for line in lines]),
                      str([line.id for line in sorted_lines]),
                      lines_text, region_text)
