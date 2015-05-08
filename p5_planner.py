__author__ = 'Kevin'

import json
from collections import namedtuple
from heapq import heappush, heappop

""" Get info from Json File """
with open('Crafting.json') as f:
    Crafting = json.load(f)

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])

""" initial setup variables """
all_recipes = []
inventory = []
item_index = {}

Items = Crafting['Items']
item_index = {name: i for i, name in enumerate(Items)}


def enum(**enums):
    return type('Enum', (), enums)


""" Makes the initial state """
def make_initial_state(inventory):
    state = inventory_to_tuple(inventory)

    return state


def make_goal_checker(goal):
    goal_tuple = inventory_to_tuple(goal)

    def is_goal(state):
        for i in range(len(state)):
            if state[i] < goal_tuple[i]:
                return False

        print "Goal reached."
        return True

    return is_goal


def make_checker(rule):
    consumes, requires = rule.get('Consumes', {}), rule.get('Requires', {})
    consume_pairs = [(item_index[item], consumes[item]) for item in consumes]
    require_pairs = [(item_index[item], 1) for item in requires]

    both_pairs = consume_pairs + require_pairs

    def check(state):
        return all([state[i] >= v for i, v in both_pairs])

    return check


def make_effector(rule):
    # sets up the effector that will effect the state when called.
    produces = rule.get('Produces', {})
    consumes = rule.get('Consumes', {})

    def effect(state):
        # this code runs millions of times
        # copy current state
        next_state = list(state)

        for i in consumes:
            next_state[item_index[i]] -= consumes[i]

        for i in produces:
            next_state[item_index[i]] += produces[i]

        return tuple(next_state)

    return effect


def graph(state):
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)

""" Tools Location in State """
Tools = [0, 1, 4, 6, 7, 12, 13, 15, 16]

""" Resources Enums """
R = enum(COAL=2, COBBLE=3, INGOT=5, ORE=8, PLANK=9, RAIL=10, STICK=11, WOOD=14)

Num = enum(BIGNUM=1000, BIGGERNUM=1000000)


def heuristic(state):
    # Check if we already have these tools
    for tool in Tools:
        if state[tool] > 1:
            return Num.BIGGERNUM

    # Check resources against max amounts for each
    if state[R.COAL] > 1 or state[R.ORE] > 1 or state[R.WOOD]:
        return Num.BIGNUM

    if state[R.COBBLE] > 8:
        return Num.BIGNUM

    if state[R.INGOT] > 6:
        return Num.BIGNUM

    if state[R.PLANK] > 7:
        return Num.BIGNUM

    if state[R.RAIL] > 32:
        return Num.BIGNUM

    if state[R.STICK] > 4:
        return Num.BIGNUM

    return 0


def inventory_to_tuple(d):
    return tuple(d.get(name, 0) for i, name in enumerate(Items))


def search(graph, initial, is_goal, limit, heuristic):
    plan = []
    visited_states = []

    curr_dist = {}
    prev_dist = {}
    curr_action = {}

    queue = []

    curr_dist[initial] = 0
    prev_dist[initial] = None
    curr_action[initial] = None

    heappush(queue, (0, initial))

    while not len(queue) == 0:

        curr_cost, curr_state = heappop(queue)

        if is_goal(curr_state):
            break

        if curr_state != initial:
            curr_cost = curr_cost - heuristic(curr_state)

        for action, next_state, next_cost in graph(curr_state):
            if next_state not in visited_states:

                temp_cost = curr_cost + next_cost

                if next_state not in curr_dist or temp_cost < curr_dist[next_state]:
                    curr_dist[next_state] = temp_cost
                    prev_dist[next_state] = curr_state
                    curr_action[next_state] = action

                    heappush(queue, (temp_cost + heuristic(next_state), next_state))

        visited_states.append(curr_state)

    total_cost = curr_dist[curr_state]

    while curr_state:
        plan.append(curr_action[curr_state])
        curr_state = prev_dist[curr_state]
    plan.reverse()

    return total_cost, plan

initial_state = make_initial_state(Crafting['Initial'])
goal = make_goal_checker(Crafting['Goal'])

for name, rule in Crafting['Recipes'].items():
    checker = make_checker(rule)
    effector = make_effector(rule)
    recipe = Recipe(name, checker, effector, rule['Time'])
    all_recipes.append(recipe)

print search(graph, initial_state, goal, 20, heuristic)







