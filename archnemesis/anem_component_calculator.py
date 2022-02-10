import json
import typing


component_formulas = {}
all_names = set()
family_tree = {}


def main():
    setup()
    print('Valid names: ')
    print(json.dumps(sorted(list(all_names)), indent=2))

    take_input = True
    while take_input:
        tool = input('Which tool would you like to use? "Recipe" or "Usage"? Or you can "quit"').lower()
        if tool == 'recipe':
            take_input = False
            recipe_loop()
        elif tool == 'usage':
            take_input = False
            usage_loop()
        elif tool == 'quit':
            take_input = False
        else:
            print('That command was not recognized.')


def recipe_loop():
    take_input = True
    while take_input:
        request = input('Request a breakdown by entering the name of an Archnemesis modifier, or type "quit":')
        if request in all_names:
            if request in component_formulas:
                result = get_subcomponents(component_formulas, request)
                while True:
                    result_format = input('Would you like this as a "tree" or a "list"?')
                    if result_format == 'tree':
                        print('Here is the full breakdown to create your component:')
                        print(json.dumps(result, indent=2))
                        break
                    elif result_format == 'list':
                        print('Here is the full list of basic subcomponents:')
                        print(json.dumps(sorted(flatten_component_tree(result)), indent=2))
                        break
                    else:
                        print('Sorry, that is not a valid command. Please try again.')
            else:
                print('That is a basic component.')
            print('You can request another breakdown.')
        elif request != 'quit':
            print('I\'m sorry, that is not a valid name from the list. Please try again.')
        else:
            take_input = False


def usage_loop():
    take_input = True
    while take_input:
        request = input('Request the usages by entering the name of an Archnemesis modifier, or type "quit":')
        if request in all_names:
            print(json.dumps(family_tree[request], indent=2))
        elif request != 'quit':
            print('I\'m sorry, that is not a valid name from the list. Please try again.')
        else:
            take_input = False


def setup():
    """Loads the formulas and the name set from resource files."""
    global component_formulas
    global all_names
    global family_tree
    with open('resources/component_formulas.json') as json_file:
        component_formulas = json.load(json_file)

    with open('resources/all_components.json') as json_file:
        all_names = set(json.load(json_file))

    with open('resources/family_tree.json') as json_file:
        family_tree = json.load(json_file)


def get_subcomponents(cfs: typing.Dict[str, typing.List[str]], request: str) -> typing.Dict[str, dict]:
    """Creates a component tree of all subcomponents of a particular component.

    Looks recursively through a component formula lookup dictionary to find all basic components.

    :param cfs: The component formulas as a dictionary of lists
    :param request: The component to look up information for.
    :return: A dictionary of dictionaries is returned, with each component showing its subcomponents.
        Basic subcomponents show an empty dictionary.
    """
    result = {}
    if request in cfs:
        for rq in cfs[request]:
            tmp = get_subcomponents(cfs, rq)
            if tmp:
                result[rq] = tmp
            else:
                result[rq] = {}
    return result


def flatten_component_tree(tree: dict) -> list:
    """Flattens a component tree into a list of its final leaves.

    Traverses the tree recursively until it meets terminating nodes, then collects all those terminating nodes
    into a list.

    :param tree: A dictionary of dictionaries any number of levels deep as returned by get_subcomponents.
    :return: A list of all entries in the input tree that had no lower-level components,
        as represented by containing only an empty dictionary for a value.
    """
    result = []
    for k, v in tree.items():
        tmp = flatten_component_tree(v)
        if tmp:
            result += tmp
        else:
            result.append(k)
    return result


def get_parents(comp_formulas: dict, names: set = None) -> dict:
    """
    Finds the chain of parents of all subcomponents,
    making a dict of all components that have the given key as a sub-component.
    """
    if names is None:
        names = flatten_component_tree(comp_formulas)
    result = {k: {} for k in names}
    for name in names:
        for k, v in comp_formulas.items():
            if name in v:
                result[name][k] = result[k]
    return result


if __name__ == '__main__':
    main()
