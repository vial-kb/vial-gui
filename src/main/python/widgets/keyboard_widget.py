from collections import defaultdict

from PyQt5.QtGui import QPainter, QColor, QPainterPath, QTransform, QBrush, QPolygonF, QPalette
from PyQt5.QtWidgets import QWidget, QToolTip, QApplication
from PyQt5.QtCore import Qt, QSize, QRect, QPointF, pyqtSignal, QEvent, QRectF, QTimer

from constants import KEY_SIZE_RATIO, KEY_SPACING_RATIO, KEYBOARD_WIDGET_PADDING, \
    KEYBOARD_WIDGET_MASK_HEIGHT, KEY_ROUNDNESS, SHADOW_SIDE_PADDING, SHADOW_TOP_PADDING, SHADOW_BOTTOM_PADDING, \
    KEYBOARD_WIDGET_NONMASK_PADDING, KEYBOARD_WIDGET_FIT_WIDTH, KEYBOARD_WIDGET_FIT_HEIGHT
from themes import Theme


class KeyWidget:

    def __init__(self, desc, scale, shift_x=0, shift_y=0):
        self.active = False
        self.on = False
        self.masked = False
        self.pressed = False
        self.desc = desc
        self.text = ""
        self.mask_text = ""
        self.tooltip = ""
        self.color = None
        self.mask_color = None
        self.scale = 0

        self.rotation_angle = desc.rotation_angle

        self.has2 = desc.width2 != desc.width or desc.height2 != desc.height or desc.x2 != 0 or desc.y2 != 0

        self.update_position(scale, shift_x, shift_y)

    def update_position(self, scale, shift_x=0, shift_y=0):
        if self.scale != scale or self.shift_x != shift_x or self.shift_y != shift_y:
            self.scale = scale
            self.size = self.scale * (KEY_SIZE_RATIO + KEY_SPACING_RATIO)
            spacing = self.scale * KEY_SPACING_RATIO

            self.rotation_x = self.size * self.desc.rotation_x
            self.rotation_y = self.size * self.desc.rotation_y

            self.shift_x = shift_x
            self.shift_y = shift_y
            self.x = self.size * self.desc.x
            self.y = self.size * self.desc.y
            self.w = self.size * self.desc.width - spacing
            self.h = self.size * self.desc.height - spacing

            self.rect = QRect(
                round(self.x),
                round(self.y),
                round(self.w),
                round(self.h)
            )
            self.text_rect = QRect(
                round(self.x),
                round(self.y + self.size * SHADOW_TOP_PADDING),
                round(self.w),
                round(self.h - self.size * (SHADOW_BOTTOM_PADDING + SHADOW_TOP_PADDING))
            )

            self.x2 = self.x + self.size * self.desc.x2
            self.y2 = self.y + self.size * self.desc.y2
            self.w2 = self.size * self.desc.width2 - spacing
            self.h2 = self.size * self.desc.height2 - spacing

            self.rect2 = QRect(
                round(self.x2),
                round(self.y2),
                round(self.w2),
                round(self.h2)
            )

            self.bbox = self.calculate_bbox(self.rect)
            self.bbox2 = self.calculate_bbox(self.rect2)
            self.polygon = QPolygonF(self.bbox + [self.bbox[0]])
            self.polygon2 = QPolygonF(self.bbox2 + [self.bbox2[0]])
            self.polygon = self.polygon.united(self.polygon2)
            self.corner = self.size * KEY_ROUNDNESS
            self.background_draw_path = self.calculate_background_draw_path()
            self.foreground_draw_path = self.calculate_foreground_draw_path()
            self.extra_draw_path = self.calculate_extra_draw_path()

            # calculate areas where the inner keycode will be located
            # nonmask = outer (e.g. Rsft_T)
            # mask = inner (e.g. KC_A)
            self.nonmask_rect = QRect(
                round(self.x),
                round(self.y + self.size * KEYBOARD_WIDGET_NONMASK_PADDING),
                round(self.w),
                round(self.h * (1 - KEYBOARD_WIDGET_MASK_HEIGHT))
            )
            self.mask_rect = QRect(
                round(self.x + self.size * SHADOW_SIDE_PADDING),
                round(self.y + self.h * (1 - KEYBOARD_WIDGET_MASK_HEIGHT)),
                round(self.w - 2 * self.size * SHADOW_SIDE_PADDING),
                round(self.h * KEYBOARD_WIDGET_MASK_HEIGHT - self.size * SHADOW_BOTTOM_PADDING)
            )
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
            t.translate(self.shift_x, self.shift_y)
            t.translate(self.rotation_x, self.rotation_y)
            t.rotate(self.rotation_angle)
            t.translate(-self.rotation_x, -self.rotation_y)
            p = t.map(QPointF(p[0], p[1]))
            bbox.append(p)
        return bbox

    def calculate_background_draw_path(self):
        path = QPainterPath()
        path.addRoundedRect(
            round(self.x),
            round(self.y),
            round(self.w),
            round(self.h),
            self.corner,
            self.corner
        )

        # second part only considered if different from first
        if self.has2:
            path2 = QPainterPath()
            path2.addRoundedRect(
                round(self.x2),
                round(self.y2),
                round(self.w2),
                round(self.h2),
                self.corner,
                self.corner
            )
            path = path.united(path2)

        return path

    def calculate_foreground_draw_path(self):
        path = QPainterPath()
        path.addRoundedRect(
            round(self.x + self.size * SHADOW_SIDE_PADDING),
            round(self.y + self.size * SHADOW_TOP_PADDING),
            round(self.w - 2 * self.size * SHADOW_SIDE_PADDING),
            round(self.h - self.size * (SHADOW_BOTTOM_PADDING + SHADOW_TOP_PADDING)),
            self.corner,
            self.corner
        )

        # second part only considered if different from first
        if self.has2:
            path2 = QPainterPath()
            path2.addRoundedRect(
                round(self.x2 + self.size * SHADOW_SIDE_PADDING),
                round(self.y2 + self.size * SHADOW_TOP_PADDING),
                round(self.w2 - 2 * self.size * SHADOW_SIDE_PADDING),
                round(self.h2 - self.size * (SHADOW_BOTTOM_PADDING + SHADOW_TOP_PADDING)),
                self.corner,
                self.corner
            )
            path = path.united(path2)

        return path

    def calculate_extra_draw_path(self):
        return QPainterPath()

    def setText(self, text):
        self.text = text

    def setMaskText(self, text):
        self.mask_text = text

    def setToolTip(self, tooltip):
        self.tooltip = tooltip

    def setActive(self, active):
        self.active = active

    def setOn(self, on):
        self.on = on

    def setPressed(self, pressed):
        self.pressed = pressed

    def setColor(self, color):
        self.color = color

    def setMaskColor(self, color):
        self.mask_color = color

    def __repr__(self):
        qualifiers = ["KeyboardWidget"]
        if self.desc.row is not None:
            qualifiers.append("matrix:{},{}".format(self.desc.row, self.desc.col))
        if self.desc.layout_index != -1:
            qualifiers.append("layout:{},{}".format(self.desc.layout_index, self.desc.layout_option))
        return " ".join(qualifiers)


class EncoderWidget(KeyWidget):

    def calculate_background_draw_path(self):
        path = QPainterPath()
        path.addEllipse(round(self.x), round(self.y), round(self.w), round(self.h))
        return path

    def calculate_foreground_draw_path(self):
        path = QPainterPath()
        path.addEllipse(
            round(self.x + self.size * SHADOW_SIDE_PADDING),
            round(self.y + self.size * SHADOW_TOP_PADDING),
            round(self.w - 2 * self.size * SHADOW_SIDE_PADDING),
            round(self.h - self.size * (SHADOW_BOTTOM_PADDING + SHADOW_TOP_PADDING))
        )
        return path

    def calculate_extra_draw_path(self):
        path = QPainterPath()
        # midpoint of arrow triangle
        p = self.h
        x = self.x
        y = self.y + p / 2
        if self.desc.encoder_dir == 0:
            # counterclockwise - pointing down
            path.moveTo(round(x), round(y))
            path.lineTo(round(x + p / 10), round(y - p / 10))
            path.lineTo(round(x), round(y + p / 10))
            path.lineTo(round(x - p / 10), round(y - p / 10))
            path.lineTo(round(x), round(y))
        else:
            # clockwise - pointing up
            path.moveTo(round(x), round(y))
            path.lineTo(round(x + p / 10), round(y + p / 10))
            path.lineTo(round(x), round(y - p / 10))
            path.lineTo(round(x - p / 10), round(y + p / 10))
            path.lineTo(round(x), round(y))
        return path

    def __repr__(self):
        return "EncoderWidget"


class KeyboardWidget(QWidget):

    clicked = pyqtSignal()
    deselected = pyqtSignal()
    anykey = pyqtSignal()

    def __init__(self, layout_editor):
        super().__init__()

        self.enabled = True
        self.scale = 1
        # how much the drawing is shrunk to fit the screen, 1 or less
        self.fit = 1
        # share of the window height the drawing may take, editors with more
        # content below the keyboard set this lower
        self.fit_height = KEYBOARD_WIDGET_FIT_HEIGHT
        self.watched = []
        self.fit_timer = QTimer(self)
        self.fit_timer.setSingleShot(True)
        self.fit_timer.timeout.connect(self.update_fit)
        self.padding = KEYBOARD_WIDGET_PADDING

        self.setMouseTracking(True)

        self.layout_editor = layout_editor

        # widgets common for all layouts
        self.common_widgets = []

        # layout-specific widgets
        self.widgets_for_layout = []

        # widgets in current layout
        self.widgets = []

        self.width = self.height = 0
        self.active_key = None
        self.active_mask = False

    def set_keys(self, keys, encoders):
        self.common_widgets = []
        self.widgets_for_layout = []

        self.add_keys([(x, KeyWidget) for x in keys] + [(x, EncoderWidget) for x in encoders])
        self.update_layout()

    def add_keys(self, keys):
        scale_factor = self.fontMetrics().height()

        for key, cls in keys:
            if key.layout_index == -1:
                self.common_widgets.append(cls(key, scale_factor))
            else:
                self.widgets_for_layout.append(cls(key, scale_factor))

    def place_widgets(self):
        scale_factor = self.fontMetrics().height()

        self.widgets = []

        # place common widgets, that is, ones which are always displayed and require no extra transforms
        for widget in self.common_widgets:
            widget.update_position(scale_factor)
            self.widgets.append(widget)

        # top-left position for specific layout
        layout_x = defaultdict(lambda: defaultdict(lambda: 1e6))
        layout_y = defaultdict(lambda: defaultdict(lambda: 1e6))

        # determine top-left position for every layout option
        for widget in self.widgets_for_layout:
            widget.update_position(scale_factor)
            idx, opt = widget.desc.layout_index, widget.desc.layout_option
            p = widget.polygon.boundingRect().topLeft()
            layout_x[idx][opt] = min(layout_x[idx][opt], p.x())
            layout_y[idx][opt] = min(layout_y[idx][opt], p.y())

        # obtain widgets for all layout options now that we know how to shift them
        for widget in self.widgets_for_layout:
            idx, opt = widget.desc.layout_index, widget.desc.layout_option
            if opt == self.layout_editor.get_choice(idx):
                shift_x = layout_x[idx][opt] - layout_x[idx][0]
                shift_y = layout_y[idx][opt] - layout_y[idx][0]
                widget.update_position(scale_factor, -shift_x, -shift_y)
                self.widgets.append(widget)

        # at this point some widgets on left side might be cutoff, or there may be too much empty space
        # calculate top left position of visible widgets and shift everything around
        top_x = top_y = 1e6
        for widget in self.widgets:
            if not widget.desc.decal:
                p = widget.polygon.boundingRect().topLeft()
                top_x = min(top_x, p.x())
                top_y = min(top_y, p.y())
        for widget in self.widgets:
            widget.update_position(widget.scale, widget.shift_x - top_x + self.padding,
                                   widget.shift_y - top_y + self.padding)

    def update_layout(self):
        """ Updates self.widgets for the currently active layout """

        # determine widgets for current layout
        self.place_widgets()
        self.widgets = list(filter(lambda w: not w.desc.decal, self.widgets))

        self.widgets.sort(key=lambda w: (w.y, w.x))

        # determine maximum width and height of container
        max_w = max_h = 0
        for key in self.widgets:
            p = key.polygon.boundingRect().bottomRight()
            max_w = max(max_w, p.x())
            max_h = max(max_h, p.y())

        self.width = round(max_w + 2 * self.padding)
        self.height = round(max_h + 2 * self.padding)
        self.schedule_fit()

        self.update()
        self.updateGeometry()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)

        # for regular keycaps
        regular_pen = qp.pen()
        regular_pen.setColor(QApplication.palette().color(QPalette.ButtonText))
        qp.setPen(regular_pen)

        background_brush = QBrush()
        background_brush.setColor(QApplication.palette().color(QPalette.Button))
        background_brush.setStyle(Qt.SolidPattern)

        foreground_brush = QBrush()
        foreground_brush.setColor(QApplication.palette().color(QPalette.Button).lighter(120))
        foreground_brush.setStyle(Qt.SolidPattern)

        mask_brush = QBrush()
        mask_brush.setColor(QApplication.palette().color(QPalette.Button).lighter(Theme.mask_light_factor()))
        mask_brush.setStyle(Qt.SolidPattern)

        # for currently selected keycap
        active_pen = qp.pen()
        active_pen.setColor(QApplication.palette().color(QPalette.Highlight))
        active_pen.setWidthF(1.5)

        # for the encoder arrow
        extra_pen = regular_pen
        extra_brush = QBrush()
        extra_brush.setColor(QApplication.palette().color(QPalette.ButtonText))
        extra_brush.setStyle(Qt.SolidPattern)

        # for pressed keycaps
        background_pressed_brush = QBrush()
        background_pressed_brush.setColor(QApplication.palette().color(QPalette.Highlight))
        background_pressed_brush.setStyle(Qt.SolidPattern)

        foreground_pressed_brush = QBrush()
        foreground_pressed_brush.setColor(QApplication.palette().color(QPalette.Highlight).lighter(120))
        foreground_pressed_brush.setStyle(Qt.SolidPattern)

        background_on_brush = QBrush()
        background_on_brush.setColor(QApplication.palette().color(QPalette.Highlight).darker(150))
        background_on_brush.setStyle(Qt.SolidPattern)

        foreground_on_brush = QBrush()
        foreground_on_brush.setColor(QApplication.palette().color(QPalette.Highlight).darker(120))
        foreground_on_brush.setStyle(Qt.SolidPattern)

        mask_font = qp.font()
        mask_font.setPointSize(round(mask_font.pointSize() * 0.8))

        for idx, key in enumerate(self.widgets):
            qp.save()

            qp.scale(self.draw_scale(), self.draw_scale())
            qp.translate(key.shift_x, key.shift_y)
            qp.translate(key.rotation_x, key.rotation_y)
            qp.rotate(key.rotation_angle)
            qp.translate(-key.rotation_x, -key.rotation_y)

            active = key.active or (self.active_key == key and not self.active_mask)

            # draw keycap background/drop-shadow
            qp.setPen(active_pen if active else Qt.NoPen)
            brush = background_brush
            if key.pressed:
                brush = background_pressed_brush
            elif key.on:
                brush = background_on_brush
            qp.setBrush(brush)
            qp.drawPath(key.background_draw_path)

            # draw keycap foreground
            qp.setPen(Qt.NoPen)
            brush = foreground_brush
            if key.pressed:
                brush = foreground_pressed_brush
            elif key.on:
                brush = foreground_on_brush
            qp.setBrush(brush)
            qp.drawPath(key.foreground_draw_path)

            # draw key text
            if key.masked:
                # draw the outer legend
                qp.setFont(mask_font)
                qp.setPen(key.color if key.color else regular_pen)
                qp.drawText(key.nonmask_rect, Qt.AlignCenter, key.text)

                # draw the inner highlight rect
                qp.setPen(active_pen if self.active_key == key and self.active_mask else Qt.NoPen)
                qp.setBrush(mask_brush)
                qp.drawRoundedRect(key.mask_rect, key.corner, key.corner)

                # draw the inner legend
                qp.setPen(key.mask_color if key.mask_color else regular_pen)
                qp.drawText(key.mask_rect, Qt.AlignCenter, key.mask_text)
            else:
                # draw the legend
                qp.setPen(key.color if key.color else regular_pen)
                qp.drawText(key.text_rect, Qt.AlignCenter, key.text)

            # draw the extra shape (encoder arrow)
            qp.setPen(extra_pen)
            qp.setBrush(extra_brush)
            qp.drawPath(key.extra_draw_path)

            qp.restore()

        qp.end()

    def draw_scale(self):
        return self.scale * self.fit

    def sizeHint(self):
        return QSize(round(self.width * self.draw_scale()), round(self.height * self.draw_scale()))

    def minimumSizeHint(self):
        return self.sizeHint()

    def schedule_fit(self):
        # coalesce the many layout events into one fit pass
        self.fit_timer.start(0)

    def watch_window(self):
        # follow the size of the window this widget is shown in
        top = self.window()
        if top is self or top in self.watched:
            return
        for w in self.watched:
            w.removeEventFilter(self)
        self.watched = [top]
        top.installEventFilter(self)

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.Resize:
            self.schedule_fit()
        return super().eventFilter(obj, ev)

    def showEvent(self, ev):
        super().showEvent(ev)
        self.watch_window()
        self.schedule_fit()

    def update_fit(self):
        # shrink the drawing when it would take more than its share of the
        # window, capped at the screen, so the whole keyboard stays visible
        # on small displays. the share is a fixed fraction rather than a
        # measurement of the other widgets, so nothing feeds back into the
        # window minimum and hidden tab pages get the right size before
        # they are shown.
        top = self.window()
        if top is self or self.width == 0 or self.height == 0:
            return

        bound_w, bound_h = top.width(), top.height()
        screen = top.screen() if hasattr(top, "screen") else None
        if screen is not None:
            avail = screen.availableGeometry()
            bound_w, bound_h = min(bound_w, avail.width()), min(bound_h, avail.height())

        fit = min(1, bound_w * KEYBOARD_WIDGET_FIT_WIDTH / (self.width * self.scale),
                  bound_h * self.fit_height / (self.height * self.scale))
        if abs(fit - self.fit) > 0.001:
            self.fit = fit
            self.updateGeometry()
            self.refresh_layouts()
            self.update()

    def refresh_layouts(self):
        # nested layouts keep their cached minimum size until their page is
        # activated, which never happens for hidden tab pages. invalidate
        # everything between this widget and the page by hand so the
        # minimums read here and by the window are current.
        def invalidate(layout):
            layout.invalidate()
            for i in range(layout.count()):
                child = layout.itemAt(i).layout()
                if child is not None:
                    invalidate(child)

        w = self.parentWidget()
        while w is not None and not w.isWindow():
            if w.layout() is not None:
                invalidate(w.layout())
            w.updateGeometry()
            w = w.parentWidget()

    def hit_test(self, pos):
        """ Returns key, hit_masked_part """

        for key in self.widgets:
            if key.masked and key.mask_polygon.containsPoint(QPointF(pos) / self.draw_scale(), Qt.OddEvenFill):
                return key, True
            if key.polygon.containsPoint(QPointF(pos) / self.draw_scale(), Qt.OddEvenFill):
                return key, False

        return None, False

    def mousePressEvent(self, ev):
        if not self.enabled:
            return

        self.active_key, self.active_mask = self.hit_test(ev.pos())
        if self.active_key is not None:
            self.clicked.emit()
        else:
            self.deselected.emit()
        self.update()

    def resizeEvent(self, ev):
        if self.isEnabled():
            self.update_layout()

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
            self.deselected.emit()
            self.update()

    def event(self, ev):
        if not self.enabled:
            super().event(ev)

        if ev.type() == QEvent.ToolTip:
            key = self.hit_test(ev.pos())[0]
            if key is not None:
                QToolTip.showText(ev.globalPos(), key.tooltip)
            else:
                QToolTip.hideText()
        elif ev.type() == QEvent.LayoutRequest:
            self.update_layout()
        elif ev.type() == QEvent.MouseButtonDblClick and self.active_key:
            self.anykey.emit()
        return super().event(ev)

    def set_enabled(self, val):
        self.enabled = val

    def set_scale(self, scale):
        self.scale = scale
        self.update_fit()
        self.updateGeometry()

    def get_scale(self):
        return self.scale
