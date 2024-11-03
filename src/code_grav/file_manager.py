import json
import os

from code_grav.nodes import Input, Output, Const, If, Operator, SubSpace, SelfSpace
from code_grav.pins import BasePin
from code_grav.space import Space, Edge
from code_grav.space_manager import SpaceManager
from code_grav.space_types import Node
from code_grav.utils import set_last_id, get_pin_by_name


def load_or_new(filepath: str):
    sm = SpaceManager(Space([('input1', '1')], [('output1', '1')]))
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return sm
    max_last_id = 0
    for n in data['nodes']:
        node = dict_to_node(sm.space, n)
        max_last_id = max(max_last_id, node.id)
        sm.space.add_node(node)
    for e in data['edges']:
        start, end = dict_to_edge(sm.space, e)
        sm.space.add_connect(start, end)
    set_last_id(max_last_id)
    return sm


def dict_to_node(space: Space, data: dict) -> Node:
    if data['name'] == 'Input':
        return Input(
            pin_events=space.sync_input_pins,
            node_id=data['id'],
            x=data['x'],
            y=data['y'],
            pins=[(pin['name'], pin['title']) for pin in data['pins']],
        )
    elif data['name'] == 'Output':
        return Output(
            pin_events=space.sync_output_pins,
            node_id=data['id'],
            x=data['x'],
            y=data['y'],
            pins=[(pin['name'], pin['title']) for pin in data['pins']],
        )
    elif data['name'] == 'Const':
        return Const(
            node_id=data['id'],
            x=data['x'],
            y=data['y'],
            value=data['value'],
        )
    elif data['name'] == 'If':
        return If(
            node_id=data['id'],
            x=data['x'],
            y=data['y'],
            value=data['value'],
        )
    elif data['name'] == 'Operator':
        return Operator(
            node_id=data['id'],
            x=data['x'],
            y=data['y'],
            value=data['value'],
        )
    elif data['name'] == 'SubSpace':
        ss = SubSpace(
            node_id=data['id'],
            x=data['x'],
            y=data['y'],
            input_pins=[(pin['name'], pin['title']) for pin in data['input_pins']],
            output_pins=[(pin['name'], pin['title']) for pin in data['output_pins']],
            space=Space(
                [(pin['name'], pin['title']) for pin in data['input_pins']],
                [(pin['name'], pin['title']) for pin in data['output_pins']],
            )
        )
        ss.space.sync_input_pins.add_handlers.append(ss.add_input_pin_handler)
        ss.space.sync_output_pins.add_handlers.append(ss.add_output_pin_handler)
        return ss
    elif data['name'] == 'SelfSpace':
        ss = SelfSpace(
            node_id=data['id'],
            x=data['x'],
            y=data['y'],
            input_pins=[(pin['name'], pin['title']) for pin in data['input_pins']],
            output_pins=[(pin['name'], pin['title']) for pin in data['output_pins']],
        )
        space.sync_input_pins.add_handlers.append(ss.add_input_pin_handler)
        space.sync_output_pins.add_handlers.append(ss.add_output_pin_handler)
        return ss
    raise NotImplemented()


def dict_to_edge(space: Space, data: dict) -> tuple[BasePin, BasePin]:
    start = space.nodes[data['start']['node_id']]
    end = space.nodes[data['end']['node_id']]
    return get_pin_by_name(start.pins, data['start']['pin_name']), get_pin_by_name(end.pins, data['end']['pin_name'])


def save(root_space: Space, filepath: str):
    data = space_to_dict(root_space)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    with open(os.path.splitext(filepath)[0] + '.g', 'w') as f:
        f.write(space_to_def(root_space))


def space_to_dict(space):
    return {
        'nodes': [
            node_to_dict(n)
            for n in space.nodes.values()
        ],
        'edges': [
            edge_to_dict(e)
            for e in space.edges
        ],
    }


def node_to_dict(node: Node) -> dict:
    if isinstance(node, Input):
        return {
            'name': 'Input',
            'id': node.id,
            'x': node.x,
            'y': node.y,
            'pins': [
                {
                    'name': pin.name,
                    'title': pin.title,
                }
                for pin in node.pins
            ],
        }
    elif isinstance(node, Output):
        return {
            'name': 'Output',
            'id': node.id,
            'x': node.x,
            'y': node.y,
            'pins': [
                {
                    'name': pin.name,
                    'title': pin.title,
                }
                for pin in node.pins
            ],
        }
    elif isinstance(node, Const):
        return {
            'name': 'Const',
            'id': node.id,
            'x': node.x,
            'y': node.y,
            'value': node.value,
        }
    elif isinstance(node, If):
        return {
            'name': 'If',
            'id': node.id,
            'x': node.x,
            'y': node.y,
            'value': node.value,
        }
    elif isinstance(node, Operator):
        return {
            'name': 'Operator',
            'id': node.id,
            'x': node.x,
            'y': node.y,
            'value': node.value,
        }
    elif isinstance(node, SubSpace):
        return {
            'name': 'SubSpace',
            'id': node.id,
            'x': node.x,
            'y': node.y,
            'input_pins': [
                {
                    'name': pin.name,
                    'title': pin.title,
                }
                for pin in node.input_pins
            ],
            'output_pins': [
                {
                    'name': pin.name,
                    'title': pin.title,
                }
                for pin in node.output_pins
            ],
            'space': space_to_dict(node.space)
        }
    elif isinstance(node, SelfSpace):
        return {
            'name': 'SelfSpace',
            'id': node.id,
            'x': node.x,
            'y': node.y,
            'input_pins': [
                {
                    'name': pin.name,
                    'title': pin.title,
                }
                for pin in node.input_pins
            ],
            'output_pins': [
                {
                    'name': pin.name,
                    'title': pin.title,
                }
                for pin in node.output_pins
            ],
        }
    raise NotImplemented()


def edge_to_dict(edge: Edge) -> dict:
    return {
        'start': {
            'node_id': edge.start.node.id,
            'pin_name': edge.start.name,
        },
        'end': {
            'node_id': edge.end.node.id,
            'pin_name': edge.end.name,
        },
    }


def space_to_def(space: Space) -> str:
    lines = []
    for n in space.nodes.values():
        lines.append(f'node_{n.id} = {node_to_def(n)}\n')
    for e in space.edges:
        lines.append(edge_to_def(e))
    return ''.join(lines)


def node_to_def(node: Node) -> str:
    if isinstance(node, Input):
        return 'input'
    elif isinstance(node, Output):
        return 'output'
    elif isinstance(node, Const):
        return f'const[{node.value}]'
    elif isinstance(node, If):
        return f'if[{node.value}]'
    elif isinstance(node, Operator):
        return f'opr[{node.value}]'
    elif isinstance(node, SubSpace):
        return f'subspace[\n{space_to_def(node.space)}]'
    elif isinstance(node, SelfSpace):
        return 'subspace[self]'
    raise NotImplemented()


def edge_to_def(edge: Edge) -> str:
    return f'{pin_to_def(edge.start)} >> {pin_to_def(edge.end)}\n'


def pin_to_def(pin: BasePin) -> str:
    if isinstance(pin.node, If):
        if not pin.name not in ['true', 'false']:
            return f'node_{pin.node.id}.{pin.name}'
    return f'node_{pin.node.id}'
