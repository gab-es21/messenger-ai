"""
Flet 0.85 API compatibility tests.
Guards against future Flet upgrades breaking constructor signatures.
Run with: python -m pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
import flet as ft


class TestPadding:
    def test_padding_all_sides(self):
        p = ft.Padding(left=16, right=16, top=12, bottom=12)
        assert p.left == 16
        assert p.right == 16
        assert p.top == 12
        assert p.bottom == 12

    def test_padding_zero(self):
        p = ft.Padding(left=0, right=0, top=0, bottom=0)
        assert p.left == 0

    def test_padding_asymmetric(self):
        p = ft.Padding(left=8, right=80, top=2, bottom=2)
        assert p.left == 8
        assert p.right == 80

    def test_no_symmetric_module_fn(self):
        """ft.padding.symmetric does not exist in 0.85 — use ft.Padding instead."""
        assert not hasattr(ft.padding, "symmetric")

    def test_no_only_module_fn(self):
        """ft.padding.only does not exist in 0.85 — use ft.Padding instead."""
        assert not hasattr(ft.padding, "only")


class TestBorder:
    def test_border_top_only(self):
        b = ft.border.Border(top=ft.BorderSide(1, "#E8E8E8"))
        assert b.top.width == 1
        assert b.top.color == "#E8E8E8"

    def test_border_top_and_bottom(self):
        b = ft.border.Border(
            top=ft.BorderSide(1, "#E8E8E8"),
            bottom=ft.BorderSide(1, "#E8E8E8"),
        )
        assert b.top.width == 1
        assert b.bottom.width == 1

    def test_border_bottom_only(self):
        b = ft.border.Border(bottom=ft.BorderSide(1, "#E8E8E8"))
        assert b.bottom.width == 1

    def test_no_border_only_fn(self):
        assert not hasattr(ft.border, "only")

    def test_no_border_symmetric_fn(self):
        assert not hasattr(ft.border, "symmetric")


class TestBorderRadius:
    def test_all_corners(self):
        br = ft.BorderRadius(top_left=4, top_right=18, bottom_left=18, bottom_right=18)
        assert br.top_left == 4
        assert br.top_right == 18

    def test_uniform(self):
        br = ft.BorderRadius(top_left=18, top_right=18, bottom_left=18, bottom_right=18)
        assert br.top_left == 18


class TestAnimation:
    def test_animation_with_curve(self):
        a = ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        assert a.duration == 200

    def test_ease_in_out_exists(self):
        assert hasattr(ft.AnimationCurve, "EASE_IN_OUT")

    def test_ease_out_exists(self):
        assert hasattr(ft.AnimationCurve, "EASE_OUT")


class TestAlignment:
    def test_center(self):
        a = ft.Alignment(0, 0)
        assert a.x == 0 and a.y == 0

    def test_center_right(self):
        a = ft.Alignment(1, 0)
        assert a.x == 1

    def test_center_left(self):
        a = ft.Alignment(-1, 0)
        assert a.x == -1

    def test_no_alignment_module_center(self):
        """ft.alignment.center does not exist — use ft.Alignment(0, 0)."""
        assert not hasattr(ft.alignment, "center")

    def test_container_accepts_alignment(self):
        c = ft.Container(alignment=ft.Alignment(0, 0))
        assert c is not None


class TestContainer:
    def test_no_max_width_param(self):
        """ft.Container has no max_width in 0.85 — omit it."""
        import inspect
        params = set(inspect.signature(ft.Container.__init__).parameters.keys())
        assert "max_width" not in params

    def test_has_width_and_height(self):
        import inspect
        params = set(inspect.signature(ft.Container.__init__).parameters.keys())
        assert "width" in params and "height" in params

    def test_construction_with_all_bubble_kwargs(self):
        c = ft.Container(
            content=ft.Text("hello"),
            bgcolor="#0084FF",
            border_radius=ft.BorderRadius(18, 18, 18, 4),
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=3, color="#00000014", offset=ft.Offset(0, 1)),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            animate_offset=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            offset=ft.Offset(0, 0.3),
            opacity=0,
        )
        assert c is not None


class TestIcons:
    def test_icons_proxy_exists(self):
        assert hasattr(ft, "Icons")

    def test_close_icon(self):
        assert ft.Icons.CLOSE is not None

    def test_send_rounded_icon(self):
        assert ft.Icons.SEND_ROUNDED is not None

    def test_settings_outlined_icon(self):
        assert ft.Icons.SETTINGS_OUTLINED is not None

    def test_play_arrow_rounded_icon(self):
        assert ft.Icons.PLAY_ARROW_ROUNDED is not None

    def test_stop_rounded_icon(self):
        assert ft.Icons.STOP_ROUNDED is not None

    def test_bubble_chart_icon(self):
        assert ft.Icons.BUBBLE_CHART is not None

    def test_no_lowercase_icons_module_attrs(self):
        """ft.icons.X doesn't work — use ft.Icons.X (uppercase I)."""
        assert not hasattr(ft.icons, "CLOSE")


class TestMiscControls:
    def test_offset(self):
        o = ft.Offset(0, 0.3)
        assert o.x == 0
        assert o.y == 0.3

    def test_box_shadow(self):
        s = ft.BoxShadow(spread_radius=0, blur_radius=3, color="#00000014", offset=ft.Offset(0, 1))
        assert s.blur_radius == 3

    def test_window_drag_area_exists(self):
        assert hasattr(ft, "WindowDragArea")

    def test_border_side_positional(self):
        bs = ft.BorderSide(1, "#E8E8E8")
        assert bs.width == 1
        assert bs.color == "#E8E8E8"
