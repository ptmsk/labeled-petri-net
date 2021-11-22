import net as ptn
import os

""" Create patient petri_net"""
place_names = ["wait", "inside", "done"]
place_objs = [ptn.Place() for _ in range(3)]

# create transitions
places = list(zip(place_names, place_objs))

transitions = dict(
    start = ptn.Transition(places, [0], [1]),
    change = ptn.Transition(places, [1], [2])
)

# create the net
p_net = ptn.PetriNet(transitions, dict(places))

if __name__ == "__main__":
    print("please enter the number of tokens in place 'wait', 'inside', 'done', respectively (The maximum number of tokens in 'wait' is 10): ")
    place_holding = [int(input().strip()) for _ in range(3)]
    place_max_token = [10, -1, -1]
    
    # set max_token
    for k, p in enumerate(p_net._places.values()):
        p._max_token = place_max_token[k]

    # set init_marking
    p_net.set_markings(place_holding)

    # print the mathematical formula for petri net
    p_net.detail_Print()
    
    # Do something
    p_net.run_debug("p_net", "asm2")