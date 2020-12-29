from collections import defaultdict

from PyQt5.QtGui import QPainter, QColor, QPainterPath, QTransform, QBrush, QPolygonF
from PyQt5.QtWidgets import QWidget, QToolTip
from PyQt5.QtCore import Qt, QSize, QRect, QPointF, pyqtSignal, QEvent, QRectF

from constants import KEY_WIDTH, KEY_SPACING, KEY_HEIGHT, KEYBOARD_WIDGET_PADDING, KEYBOARD_WIDGET_MASK_PADDING


class KeyWidget:

    def __init__(self, desc, shift_x=0, shift_y=0):
        self.desc = desc
        self.text = ""
        self.mask_text = ""
        self.tooltip = ""

        self.rotation_x = (KEY_WIDTH + KEY_SPACING) * desc.rotation_x
        self.rotation_y = (KEY_HEIGHT + KEY_SPACING) * desc.rotation_y
        self.rotation_angle = desc.rotation_angle

        self.x = shift_x + (KEY_WIDTH + KEY_SPACING) * desc.x
        self.y = shift_y + (KEY_HEIGHT + KEY_SPACING) * desc.y
        self.w = (KEY_WIDTH + KEY_SPACING) * desc.width - KEY_SPACING
        self.h = (KEY_HEIGHT + KEY_SPACING) * desc.height - KEY_SPACING

        self.rect = QRect(self.x, self.y, self.w, self.h)

        self.has2 = desc.width2 != desc.width or desc.height2 != desc.height or desc.x2 != 0 or desc.y2 != 0

        self.x2 = self.x + (KEY_WIDTH + KEY_SPACING) * desc.x2
        self.y2 = self.y + (KEY_WIDTH + KEY_SPACING) * desc.y2
        self.w2 = (KEY_WIDTH + KEY_SPACING) * desc.width2 - KEY_SPACING
        self.h2 = (KEY_HEIGHT + KEY_SPACING) * desc.height2 - KEY_SPACING

        self.bbox = self.calculate_bbox(QRectF(self.x, self.y, self.w, self.h))
        self.polygon = QPolygonF(self.bbox + [self.bbox[0]])
        self.draw_path = self.calculate_draw_path()
        self.draw_path2 = self.calculate_draw_path2()

        # calculate areas where the inner keycode will be located
        # nonmask = outer (e.g. Rsft_T)
        # mask = inner (e.g. KC_A)
        self.nonmask_rect = QRectF(self.x, self.y, self.w, self.h / 2)
        self.mask_rect = QRectF(self.x + KEYBOARD_WIDGET_MASK_PADDING, self.y + self.h / 2,
                                self.w - 2 * KEYBOARD_WIDGET_MASK_PADDING, self.h / 2 - KEYBOARD_WIDGET_MASK_PADDING)
        self.mask_bbox = self.calculate_bbox(self.mask_rect)
        self.mask_polygon = QPolygonF(self.mask_bbox + [self.mask_bbox[0]])

    def calculate_bbox(self, rect):
        x1 = rect.topLeft().x()
        y1 = rect.topLeft().y()
        x2 = rect.bottomRight().x()
        y2 = rect.bottomRight().y()
        points = [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]
        bbox = []
        for p in points:
            t = QTransform()
            t.translate(KEYBOARD_WIDGET_PADDING, KEYBOARD_WIDGET_PADDING)
            t.translate(self.rotation_x, self.rotation_y)
            t.rotate(self.rotation_angle)
            t.translate(-self.rotation_x, -self.rotation_y)
            p = t.map(QPointF(p[0], p[1]))
            bbox.append(p)
        return bbox

    def calculate_draw_path(self):
        path = QPainterPath()
        path.addRect(int(self.x), int(self.y), int(self.w), int(self.h))

        # second part only considered if different from first
        if self.has2:
            path2 = QPainterPath()
            path2.addRect(int(self.x2), int(self.y2), int(self.w2), int(self.h2))
            path = path.united(path2)

        return path

    def calculate_draw_path2(self):
        return QPainterPath()

    def setText(self, text):
        self.text = text

    def setMaskText(self, text):
        self.mask_text = text

    def setToolTip(self, tooltip):
        self.tooltip = tooltip


class EncoderWidget(KeyWidget):

    def calculate_draw_path(self):
        path = QPainterPath()
        path.addEllipse(int(self.x), int(self.y), int(self.w), int(self.h))
        return path

    def calculate_draw_path2(self):
        path = QPainterPath()
        if self.desc.encoder_dir == 0:
            path.moveTo(int(self.x), int(self.y + self.h / 2))
            path.lineTo(int(self.x - self.w / 5), int(self.y + self.h / 3))
            path.moveTo(int(self.x), int(self.y + self.h / 2))
            path.lineTo(int(self.x + self.w / 5), int(self.y + self.h / 3))
        else:
            path.moveTo(int(self.x), int(self.y + self.h / 2))
            path.lineTo(int(self.x - self.w / 5), int(self.y + self.h - self.h / 3))
            path.moveTo(int(self.x), int(self.y + self.h / 2))
            path.lineTo(int(self.x + self.w / 5), int(self.y + self.h - self.h / 3))
        return path


class KeyboardWidget(QWidget):

    clicked = pyqtSignal()

    def __init__(self, layout_editor):
        super().__init__()
        self.setMouseTracking(True)

        self.layout_editor = layout_editor

        # widgets common for all layouts
        self.common_widgets = []

        # layout-specific widgets
        self.widgets_for_layout = defaultdict(lambda: defaultdict(list))

        # widgets in current layout
        self.widgets = []

        self.width = self.height = 0
        self.active_key = None
        self.active_mask = False

    def set_keys(self, keys, encoders):
        self.common_widgets = []
        self.widgets_for_layout = defaultdict(lambda: defaultdict(list))

        self.add_keys([(x, KeyWidget) for x in keys] + [(x, EncoderWidget) for x in encoders])
        self.update_layout()

    def add_keys(self, keys):
        top_x = top_y = 1e6

        # find the global top-left position, all the keys will be shifted to the left/up by that position
        for key, cls in keys:
            if key.layout_index == -1:
                obj = cls(key)
                top_x = min(top_x, obj.x)
                top_y = min(top_y, obj.y)

        # obtain common widgets, that is, ones which are always displayed and require no extra transforms
        for key, cls in keys:
            if key.layout_index == -1:
                self.common_widgets.append(cls(key, -top_x, -top_y))

        # top-left position for specific layout
        layout_x = defaultdict(lambda: defaultdict(lambda: 1e6))
        layout_y = defaultdict(lambda: defaultdict(lambda: 1e6))

        # determine top-left position for every layout option
        for key, cls in keys:
            if key.layout_index != -1:
                obj = cls(key)
                idx, opt = key.layout_index, key.layout_option
                layout_x[idx][opt] = min(layout_x[idx][opt], obj.x)
                layout_y[idx][opt] = min(layout_y[idx][opt], obj.y)

        # obtain widgets for all layout options now that we know how to shift them
        for key, cls in keys:
            if key.layout_index != -1:
                idx, opt = key.layout_index, key.layout_option
                shift_x = layout_x[idx][opt] - layout_x[idx][0]
                shift_y = layout_y[idx][opt] - layout_y[idx][0]
                obj = cls(key, -shift_x - top_x, -shift_y - top_y)
                self.widgets_for_layout[idx][opt].append(obj)

    def update_layout(self):
        """ Updates self.widgets for the currently active layout """

        # determine widgets for current layout
        self.widgets = []
        self.widgets += self.common_widgets
        for idx in self.widgets_for_layout.keys():
            option = self.layout_editor.get_choice(idx)
            self.widgets += self.widgets_for_layout[idx][option]

        self.widgets = list(filter(lambda w: not w.desc.decal, self.widgets))

        self.widgets.sort(key=lambda w: (w.y, w.x))

        # determine maximum width and height of container
        max_w = max_h = 0
        for key in self.widgets:
            p = key.polygon.boundingRect().bottomRight()
            max_w = max(max_w, p.x())
            max_h = max(max_h, p.y())

        self.width = max_w + 2 * KEYBOARD_WIDGET_PADDING
        self.height = max_h + 2 * KEYBOARD_WIDGET_PADDING

        self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)

        # add a little padding
        qp.translate(KEYBOARD_WIDGET_PADDING, KEYBOARD_WIDGET_PADDING)

        # for regular keycaps
        regular_pen = qp.pen()
        regular_pen.setColor(QColor("black"))
        qp.setPen(regular_pen)

        regular_brush = QBrush()
        regular_brush.setColor(QColor("white"))
        regular_brush.setStyle(Qt.SolidPattern)
        qp.setBrush(regular_brush)

        # for currently selected keycap
        active_pen = qp.pen()
        active_pen.setColor(QColor("white"))

        active_brush = QBrush()
        active_brush.setColor(QColor("black"))
        active_brush.setStyle(Qt.SolidPattern)

        mask_font = qp.font()
        mask_font.setPointSize(mask_font.pointSize() * 0.8)

        for idx, key in enumerate(self.widgets):
            qp.save()
            qp.translate(key.rotation_x, key.rotation_y)
            qp.rotate(key.rotation_angle)
            qp.translate(-key.rotation_x, -key.rotation_y)

            if self.active_key == key and not self.active_mask:
                qp.setPen(active_pen)
                qp.setBrush(active_brush)

            # draw the keycap
            qp.drawPath(key.draw_path)
            qp.strokePath(key.draw_path2, regular_pen)

            # if this is a mask key, draw the inner key
            if key.masked:
                qp.setFont(mask_font)
                qp.drawText(key.nonmask_rect, Qt.AlignCenter, key.text)

                if self.active_key == key and self.active_mask:
                    qp.setPen(active_pen)
                    qp.setBrush(active_brush)

                qp.drawRect(key.mask_rect)
                qp.drawText(key.mask_rect, Qt.AlignCenter, key.mask_text)
            else:
                # draw the legend
                qp.drawText(key.rect, Qt.AlignCenter, key.text)

            qp.restore()

        qp.end()

    def minimumSizeHint(self):
        return QSize(self.width, self.height)

    def hit_test(self, pos):
        """ Returns key, hit_masked_part """

        for key in self.widgets:
            if key.masked and key.mask_polygon.containsPoint(pos, Qt.OddEvenFill):
                return key, True
            if key.polygon.containsPoint(pos, Qt.OddEvenFill):
                return key, False

        return None, False

    def mousePressEvent(self, ev):
        self.active_key, self.active_mask = self.hit_test(ev.pos())
        if self.active_key is not None:
            self.clicked.emit()
        self.update()

    def select_next(self):
        """ Selects next key based on their order in the keymap """

        keys_looped = self.widgets + [self.widgets[0]]
        for x, key in enumerate(keys_looped):
            if key == self.active_key:
                self.active_key = keys_looped[x + 1]
                self.active_mask = False
                self.clicked.emit()
                return

    def deselect(self):
        if self.active_key is not None:
            self.active_key = None
            self.update()

    def event(self, ev):
        if ev.type() == QEvent.ToolTip:
            key = self.hit_test(ev.pos())[0]
            if key is not None:
                QToolTip.showText(ev.globalPos(), key.tooltip)
            else:
                QToolTip.hideText()
        return super().event(ev)
