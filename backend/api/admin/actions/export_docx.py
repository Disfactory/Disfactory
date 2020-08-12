import os
from io import BytesIO
from urllib.request import urlopen

from django.http import HttpResponse

from api.models import Image

from docx import Document
from docx.shared import Inches, Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

from docxcompose.composer import Composer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_RESOURCES_PATH = os.path.join(
    CURRENT_DIR, "..", "..", "..", "doc_resources")
SEAL_IMAGE_PATH = os.path.join(DOC_RESOURCES_PATH, "seal.png")

DEFAULT_FONT = "標楷體"

UPPER_CASE_NUMBERS = {
    "0": '零',
    "1": '壹',
    "2": '貳',
    "3": '參',
    "4": '肆',
    "5": '伍',
    "6": '陸',
    "7": '柒',
    "8": '捌',
    "9": '玖'
}

LOWER_CASE_NUMBERS = {
    "0": '〇',
    "1": '一',
    "2": '二',
    "3": '三',
    "4": '四',
    "5": '五',
    "6": '六',
    "7": '七',
    "8": '八',
    "9": '九'
}


def ConvertToUpperCaseNumbers(number):
    result = list(map(lambda s: UPPER_CASE_NUMBERS[s], str(number)))
    return ''.join(result)


def ConvertToLowerCaseNumbers(number):
    result = list(map(lambda s: LOWER_CASE_NUMBERS[s], str(number)))
    return ''.join(result)


class Run:
    def __init__(self, context, size):
        self._context = context
        self._size = size

    def new(self, paragraph):
        run = paragraph.add_run(self._context)
        run.font.size = Pt(self._size)
        return run


class ParagraphGenerator:
    ALIGN_LEFT = WD_ALIGN_PARAGRAPH.LEFT
    ALIGN_CENTER = WD_ALIGN_PARAGRAPH.CENTER
    ALIGN_RIGHT = WD_ALIGN_PARAGRAPH.RIGHT

    def __init__(self):
        self._alignment = None
        self._line_spacing = None
        self._space_before = None
        self._space_after = None
        self._first_line_indent = None
        self._left_indent = None

    def new(self, document, context, font_size):
        paragraph = document.add_paragraph()
        if self._alignment is not None:
            paragraph.paragraph_format.alignment = self._alignment

        if self._line_spacing is not None:
            paragraph.paragraph_format.line_spacing = self._line_spacing

        if self._space_before is not None:
            paragraph.paragraph_format.space_before = self._space_before

        if self._space_after is not None:
            paragraph.paragraph_format.space_after = self._space_after

        if self._left_indent is not None:
            paragraph.paragraph_format.left_indent = self._left_indent

        if self._first_line_indent is not None:
            paragraph.paragraph_format.first_line_indent = self._first_line_indent

        run = Run(context, font_size)
        run.new(paragraph)

        return paragraph

    def alignment(self, alignment):
        self._alignment = alignment
        return self

    def line_spacing(self, size):
        self._line_spacing = Pt(size)
        return self

    def space_after(self, size):
        self._space_after = Pt(size)
        return self

    def space_before(self, size):
        self._space_before = Pt(size)
        return self

    def left_indent(self, inches_size):
        self._left_indent = Inches(inches_size)
        return self

    def first_line_indent(self, inches_size):
        self._first_line_indent = Inches(inches_size)
        return self


class FactoryReportDocumentWriter:
    def __init__(self, factory, document):
        self.factory = factory
        self.document = document
        self.factory_location = f"{self.factory.townname}({self.factory.sectcode}) {self.factory.landcode}"

        self._generate_docx()

    def _init_document(self):
        # Change layout
        section = self.document.sections[0]

        # Margins
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

        # A4 paper
        section.page_height = Mm(297)
        section.page_width = Mm(210)

    def _generate_docx(self):
        self._init_document()

        # Cover
        self._title()
        self._sender()
        self._receiver("00000000000")
        self._subject()
        self._context()
        self._cc("UNKNOWN")
        self._seal()

        self._page_break()

        # Attachments
        self._attchments()

    def _title(self):
        generator = ParagraphGenerator() \
            .alignment(ParagraphGenerator.ALIGN_CENTER) \
            .line_spacing(20) \
            .space_before(6) \
            .space_after(0)

        generator.new(self.document, "地球公民基金會 函", 20)
        generator.new(self.document, "", 20)

    def _sender(self):
        context = [
            '地址：10049台北市北平東路28號9樓之2',
            '電話：02-23920371 ',
            '傳真：02-23920381',
            '連絡人：吳沅諭',
            '電子信箱：eva@cet-taiwan.org'
        ]

        generator = ParagraphGenerator() \
            .alignment(ParagraphGenerator.ALIGN_RIGHT) \
            .line_spacing(15) \
            .space_after(0)

        for line in context:
            generator.new(self.document, line, 10)

    def _receiver(self, serial):
        context = [
            '',
            '受文者：如正、副本行文單位',
            '發文日期：中華民國109年6月31日',
            f'發文字號：地球公民違字第 {serial} 號',
            '速別：普通件',
            '附件：舉證照片',
            ''
        ]

        generator = ParagraphGenerator() \
            .alignment(ParagraphGenerator.ALIGN_LEFT) \
            .line_spacing(21) \
            .space_after(0)

        for line in context:
            generator.new(self.document, line, 14)

    def _subject(self):
        context = [
            f'主旨：舉報 {self.factory_location} 地號土地疑有違法新增建築情事。',
            '',
            '說明：'
        ]

        generator = ParagraphGenerator() \
            .alignment(ParagraphGenerator.ALIGN_LEFT) \
            .line_spacing(21) \
            .space_after(0)

        for line in context:
            generator.new(self.document, line, 14)

    def _context(self):
        context = [
            '一、　依工廠管理輔導法第28-1、28-12條辦理。',
            f"二、　{self.factory_location} 地號土地新發現新增建情形，經地球公民基金會志工拍攝存證，如附件一。因懷疑係屬非法建築行為，函請貴府調查處理。若有不法情事，並應依法裁處，請貴府將查處情形，惠知本會。"
        ]

        generator = ParagraphGenerator() \
            .alignment(ParagraphGenerator.ALIGN_LEFT) \
            .line_spacing(21) \
            .space_after(0)

        for line in context:
            generator.new(self.document, line, 14)

    def _cc(self, legislator):
        townname = self.factory.townname
        if townname:
            townname = townname[:3]
        else:
            townname = "UNKNOWN"
        context = [
            '',
            f"正本：{townname} 政府",
            f"副本：內政部、行政院農委會、經濟部工業局、經濟部中部辦公室、立法委員 {legislator} 國會辦公室"
        ]

        generator = ParagraphGenerator() \
            .alignment(ParagraphGenerator.ALIGN_LEFT) \
            .line_spacing(12) \
            .space_after(0)

        for line in context:
            generator.new(self.document, line, 12)

    def _seal(self):
        self.document.add_picture(SEAL_IMAGE_PATH, width=Inches(4.5))
        paragraph = self.document.paragraphs[-1]
        paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        paragraph.paragraph_format.space_before = Inches(0.7)

    def _attchments(self):
        generator = ParagraphGenerator() \
            .alignment(ParagraphGenerator.ALIGN_LEFT) \
            .line_spacing(18) \
            .space_after(6)

        images = Image.objects.only("id").filter(factory=self.factory)
        for index, image in enumerate(images, start=1):
            generator.new(
                self.document, f"附件 {ConvertToLowerCaseNumbers(index)}", 12)
            data = urlopen(image.image_path).read()
            self.document.add_picture(BytesIO(data), width=Mm(150))

    def _page_break(self):
        self.document.add_page_break()


def new_document():
    document = Document()
    document.styles['Normal'].font.name = DEFAULT_FONT
    document.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), DEFAULT_FONT)
    return document


def generate_factories_document(factories):
    documents = []
    for factory in factories:
        document = new_document()
        FactoryReportDocumentWriter(factory, document)
        documents.append(document)
    return documents


def merge_documents(documents):
    for document in documents[:-1]:
        document.add_page_break()

    composer = Composer(documents[0])

    for document in documents[1:]:
        composer.append(document)

    return composer.doc


def export_document(document):
    file = BytesIO()
    document.save(file)

    return file


class ExportDocMixin:
    def export_as_docx(self, request, queryset):
        documents = generate_factories_document(list(queryset))
        merged_docment = merge_documents(documents)
        docx_file = export_document(merged_docment)

        length = docx_file.tell()
        docx_file.seek(0)

        response = HttpResponse(
            docx_file.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename=' + \
            'api.factory.docx'
        response['Content-Length'] = length
        return response

    export_as_docx.short_description = '輸出成 docx 檔'
