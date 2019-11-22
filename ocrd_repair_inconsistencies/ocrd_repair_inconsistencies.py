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

TOOL = 'ocrd_repair_inconsistencies'
LOG = getLogger('processor.RepairInconsistencies')

class RepairInconsistencies(Processor):

    def __init__(self, *args, **kwargs):
        kwargs['ocrd_tool'] = OCRD_TOOL['tools'][TOOL]
        super(RepairInconsistencies, self).__init__(*args, **kwargs)

    def _fix_lines(self, region):
        """Fix line order in a region"""

        lines = region.get_TextLine()
        region_text = get_text(region)
        lines_text = get_text(lines, '\n')
        if region_text != lines_text:
            # XXX Assumes top-to-bottom
            sorted_lines = sorted(lines, key=lambda l: Polygon(polygon_from_points(l.get_Coords().points)).centroid.y)
            sorted_lines_text = get_text(sorted_lines, '\n')

            if sorted_lines_text == region_text:
                LOG.info('Fixing line order of region "%s"', region.id)
                region.set_TextLine(sorted_lines)

    def _fix_words(self, line):
        """Fix word order in a line"""

        words = line.get_Word()
        line_text = get_text(line)
        words_text = get_text(words, ' ')
        if line_text != words_text:
            # XXX Assumes left-to-right
            sorted_words = sorted(words, key=lambda w: Polygon(polygon_from_points(w.get_Coords().points)).centroid.x)
            sorted_words_text = get_text(sorted_words, ' ')

            if sorted_words_text == line_text:
                LOG.info('Fixing word order of line "%s"', line.id)
                line.set_Word(sorted_words)

    def _fix_glyphs(self, word):
        """Fix glyph order in a word"""

        glyphs = word.get_Glyph()
        word_text = get_text(word)
        glyphs_text = get_text(glyphs, '')
        if word_text != glyphs_text:
            # XXX Assumes left-to-right
            sorted_glyphs = sorted(glyphs, key=lambda g: Polygon(polygon_from_points(g.get_Coords().points)).centroid.x)
            sorted_glyphs_text = get_text(sorted_glyphs, '')

            if sorted_glyphs_text == word_text:
                LOG.info('Fixing glyph order of word "%s"', word.id)
                word.set_Glyph(sorted_glyphs)

    def process(self):
        for (n, input_file) in enumerate(self.input_files):
            page_id = input_file.pageId or input_file.ID
            LOG.info("INPUT FILE %i / %s", n, page_id)
            pcgts = page_from_file(self.workspace.download_file(input_file))
            page = pcgts.get_Page()


            regions = page.get_TextRegion()
            for region in regions:
                self._fix_lines(region)

                lines = region.get_TextLine()
                for line in lines:
                    self._fix_words(line)

                    words = line.get_Word()
                    for word in words:
                        self._fix_glyphs(word)

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
        # XXX Assumes len(TextEquiv) == 1
        try:
            return t.get_TextEquiv()[0].get_Unicode()
        except Exception:
            return None

    if isinstance(thing, Sequence):
        text = joiner.join(_get_text_for_one(t) for t in thing)
    else:
        text = _get_text_for_one(thing)
    return text