import json
import pygame
from ui.mask_colors import mask_colors


OWNER_COLORS = {
    -1: (160, 160, 160, 90),   # neutral
    0: (80, 140, 255, 110),    # blue
    1: (255, 90, 90, 110),     # red
    2: (90, 220, 120, 110),    # green
    3: (255, 255, 80, 110),    # yellow
    4: (190, 120, 255, 110),   # purple
    5: (255, 170, 70, 110),    # orange
}


BADGE_COLORS = {
    -1: (180, 180, 180),
    0: (80, 140, 255),
    1: (255, 90, 90),
    2: (90, 220, 120),
    3: (240, 220, 80),
    4: (190, 120, 255),
    5: (255, 170, 70),
}


def load_map_data(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def hex_to_rgb(hex_string):
    value = hex_string.lstrip("#")
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return (red, green, blue)


def build_territory_templates(mask_surface, territories):
    templates = {}

    for territory in territories:
        name = territory["name"]
        rgb = hex_to_rgb(mask_colors[int(name)][0])
        rgba = (rgb[0], rgb[1], rgb[2], 255)

        territory_mask = pygame.mask.from_threshold(
            mask_surface,
            rgba,
            threshold=(1, 1, 1)
        )

        template = territory_mask.to_surface(
            setcolor=(255, 255, 255, 255),
            unsetcolor=(0, 0, 0, 0)
        ).convert_alpha()

        templates[name] = template

    return templates


def tint_template(template, color_rgba):
    tinted = template.copy()
    tinted.fill(color_rgba, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


def draw_owner_overlays(screen, templates, territories):
    for territory in territories.values():
        name = territory.name
        owner_id = territory.owner_id
        color = OWNER_COLORS.get(owner_id, OWNER_COLORS[-1])

        template = templates[name]
        overlay = tint_template(template, color)
        screen.blit(overlay, (0, 0))


def draw_army_counts(screen, territories, font, scale):
    for territory in territories.values():
        x, y = mask_colors[int(territory.name)][1]
        x *= scale
        y *= scale
        owner_id = territory.owner_id
        armies = territory.armies

        badge_color = BADGE_COLORS.get(owner_id, BADGE_COLORS[-1])

        pygame.draw.circle(screen, badge_color, (x, y), 18)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), 18, 2)

        text = font.render(str(armies), True, (0, 0, 0))
        rect = text.get_rect(center=(x, y))
        screen.blit(text, rect)


def draw_board_state(screen, board_surface, templates, territories, font, scale):
    screen.blit(board_surface, (0, 0))
    draw_owner_overlays(screen, templates, territories)
    draw_army_counts(screen, territories, font, scale)