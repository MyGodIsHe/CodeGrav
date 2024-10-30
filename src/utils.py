from nodes import Node


_LAST_ID = 0


def normalize_rect(rect):
    if rect.width < 0:
        rect.x += rect.width
        rect.width = abs(rect.width)
    if rect.height < 0:
        rect.y += rect.height
        rect.height = abs(rect.height)
    return rect


def get_common_center(nodes: list[Node]):
    assert nodes
    total_x, total_y = 0, 0

    for node in nodes:
        center = node.select_rect().center
        total_x += center[0]
        total_y += center[1]

    common_center_x = total_x // len(nodes)
    common_center_y = total_y // len(nodes)

    return common_center_x, common_center_y


def get_new_id() -> int:
    global _LAST_ID
    _LAST_ID += 1
    return _LAST_ID
