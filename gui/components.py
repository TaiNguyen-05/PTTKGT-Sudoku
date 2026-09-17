"""
Reusable UI Components for the Pygame Interface:
Button, Slider, TabBar, and MetricsCard with modern styling and smooth hover interactions.
"""
import pygame
from typing import Callable, Optional, Tuple, List
from gui.constants import (
    COLOR_BG, COLOR_SURFACE, COLOR_SURFACE_LIGHT, COLOR_BORDER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED, COLOR_TEXT_ACCENT, COLOR_BTN_PRIMARY, COLOR_BTN_PRIMARY_HOVER,
    COLOR_BTN_SECONDARY, COLOR_BTN_SECONDARY_HOVER
)


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        text: str,
        on_click: Optional[Callable[[], None]] = None,
        bg_color: Tuple[int, int, int] = COLOR_BTN_SECONDARY,
        hover_color: Tuple[int, int, int] = COLOR_BTN_SECONDARY_HOVER,
        text_color: Tuple[int, int, int] = COLOR_TEXT_PRIMARY,
        font_size: int = 18,
        border_radius: int = 8,
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.on_click = on_click
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.border_radius = border_radius
        self.is_hovered = False
        self.enabled = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        color = self.hover_color if (self.is_hovered and self.enabled) else self.bg_color
        if not self.enabled:
            color = (color[0] // 2, color[1] // 2, color[2] // 2)

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, COLOR_BORDER, self.rect, width=1, border_radius=self.border_radius)

        txt_surf = font.render(self.text, True, self.text_color if self.enabled else COLOR_TEXT_MUTED)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)


class Slider:
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        min_val: float,
        max_val: float,
        initial_val: float,
        label: str = "",
        on_change: Optional[Callable[[float], None]] = None,
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.on_change = on_change
        self.dragging = False
        self.handle_radius = 9

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_val_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_val_from_mouse(event.pos[0])
            return True
        return False

    def _update_val_from_mouse(self, mouse_x: int) -> None:
        rel_x = max(0, min(self.rect.width, mouse_x - self.rect.x))
        ratio = rel_x / self.rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        if self.on_change:
            self.on_change(self.val)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        # Nhãn
        label_text = f"{self.label}: {int(self.val)} fps" if "Tốc độ" in self.label else f"{self.label}: {self.val:.1f}"
        lbl_surf = font.render(label_text, True, COLOR_TEXT_PRIMARY)
        surface.blit(lbl_surf, (self.rect.x, self.rect.y - 22))

        # Đường trượt
        pygame.draw.rect(surface, COLOR_SURFACE_LIGHT, self.rect, border_radius=4)
        
        # Phần đã trượt
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        fill_w = int(self.rect.width * ratio)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
        pygame.draw.rect(surface, COLOR_BTN_PRIMARY, fill_rect, border_radius=4)

        # Nút tròn kéo
        handle_x = self.rect.x + fill_w
        handle_y = self.rect.centery
        pygame.draw.circle(surface, COLOR_TEXT_PRIMARY, (handle_x, handle_y), self.handle_radius)
        pygame.draw.circle(surface, COLOR_BTN_PRIMARY, (handle_x, handle_y), self.handle_radius - 2)


class TabBar:
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        tabs: List[str],
        on_tab_select: Optional[Callable[[int], None]] = None,
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.tabs = tabs
        self.selected_index = 0
        self.on_tab_select = on_tab_select

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                tab_w = self.rect.width / len(self.tabs)
                clicked_idx = int((event.pos[0] - self.rect.x) // tab_w)
                if 0 <= clicked_idx < len(self.tabs):
                    self.selected_index = clicked_idx
                    if self.on_tab_select:
                        self.on_tab_select(clicked_idx)
                    return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        tab_w = self.rect.width / len(self.tabs)
        for i, title in enumerate(self.tabs):
            tab_rect = pygame.Rect(self.rect.x + i * tab_w, self.rect.y, tab_w, self.rect.height)
            is_active = (i == self.selected_index)

            # Nền tab
            bg_col = COLOR_SURFACE if is_active else COLOR_BG
            pygame.draw.rect(surface, bg_col, tab_rect, border_top_left_radius=8, border_top_right_radius=8)

            # Thanh active indicator bên dưới
            if is_active:
                ind_rect = pygame.Rect(tab_rect.x, tab_rect.bottom - 3, tab_rect.width, 3)
                pygame.draw.rect(surface, COLOR_BTN_PRIMARY, ind_rect)

            # Chữ tiêu đề
            txt_col = COLOR_TEXT_ACCENT if is_active else COLOR_TEXT_MUTED
            txt_surf = font.render(title, True, txt_col)
            txt_rect = txt_surf.get_rect(center=tab_rect.center)
            surface.blit(txt_surf, txt_rect)
