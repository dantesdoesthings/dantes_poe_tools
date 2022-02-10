import json
import typing
import re


component_formulas = {}
all_names = set()
family_tree = {}
name_lookup_table = {}


def main():
    setup()
    print('Valid names: ')
    print(json.dumps(sorted(list(all_names)), indent=2))

    take_input = True
    while take_input:
        tool = clean_input(input('Which tool would you like to use? "Recipe" or "Usage"? Or you can "quit"\n'))
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
        request = clean_input(input('Request a breakdown by entering the name '
                                     'of an Archnemesis modifier, or type "quit":\n'))
        if request in name_lookup_table:
            if name_lookup_table[request] in component_formulas:
                result = get_subcomponents(component_formulas, request)
                while True:
                    result_format = input('Would you like this as a "tree" or a "list"?\n')
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
        request = clean_input(input('Request the usages by entering the name of '
                                     'an Archnemesis modifier, or type "quit":\n'))
        if request in name_lookup_table:
            result = family_tree[name_lookup_table[request]]
            if result:
                print(json.dumps(result, indent=2))
            else:
                print("No further usages for that component.")
        elif request != 'quit':
            print('I\'m sorry, that is not a valid name from the list. Please try again.')
        else:
            take_input = False


def setup():
    """Loads the formulas and the name set from resource files."""
    global component_formulas
    global all_names
    global family_tree
    global name_lookup_table
    with open('resources/component_formulas.json') as json_file:
        component_formulas = json.load(json_file)

    with open('resources/all_components.json') as json_file:
        all_names = set(json.load(json_file))

    with open('resources/family_tree.json') as json_file:
        family_tree = json.load(json_file)

    with open('resources/name_lookup_table.json') as json_file:
        name_lookup_table = json.load(json_file)


def get_subcomponents(cfs: typing.Dict[str, typing.List[str]], request: str) -> typing.Dict[str, dict]:
    """Creates a component tree of all subcomponents of a particular component.

    Looks recursively through a component formula lookup dictionary to find all basic components.

    :param cfs: The component formulas as a dictionary of lists
    :param request: The component to look up information for.
    :return: A dictionary of dictionaries is returned, with each component showing its subcomponents.
        Basic subcomponents show an empty dictionary.
    """
    if request in name_lookup_table:
        request = name_lookup_table[request]
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


def generate_lookup_table(original_names: set) -> dict:
    """Takes a set of names and generates a lookup table of lowercase, stripped keys pointing to the original names."""
    return {clean_input(name) : name for name in original_names}


def clean_input(name: str) -> str:
    """Processes a name, stripping non-letter characters and lower-casing them."""
    return re.sub(r'[^a-z]+', '', name.lower())


if __name__ == '__main__':
    main()
