import net as ptn
import os
import graphviz

""" Create specialist petri net """
# create places
place_names = ["free", "busy", "docu"]
place_objs = [ptn.Place() for _ in range(3)]

# create transitions
places = list(zip(place_names, place_objs))

transitions = dict(
    start = ptn.Transition(places, [0], [1]),
    change = ptn.Transition(places, [1], [2]),
    end = ptn.Transition(places, [2], [0])
)

# create the net
s_net = ptn.PetriNet(transitions, dict(places))

if __name__ == "__main__":
    """ ---------- 1.b (i) ---------- """   
    # Create transition system from the net above with maximum 1 tokens at each place
    print("\n1.b.(i): Create transition system from the net above with maximum 1 token\n")
    max_token = 1
    # set max_token
    for p in s_net._places.values():
        p._max_token = max_token

    init_marking = [1, 0, 0]
    print("Initial marking: [1.free]\n")
    s_net.set_markings(init_marking)

    # find all firing rules:
    firing_rules = s_net.run_sequent()

    # find all markings at states and all transitions in the new transition
    states = set()
    transitions = set()
    print("All firing rules: ")
    for trans in firing_rules:
        states.add("[" + ", ".join([trans[0][i] for i in range(len(trans[0]))]) + "]")
        states.add("[" + ", ".join([trans[2][i] for i in range(len(trans[2]))]) + "]")
        transitions.add(trans[1][0])
        print("[", ", ".join([trans[0][i] for i in range(len(trans[0]))]), "]", end="  ", sep="")
        print("[", trans[1][0], ">", "  [", ", ".join([trans[2][i] for i in range(len(trans[2]))]), "]", sep="")

    print("All states: ", "; ".join([st for st in states]))
    print("All transitions: ", "; ".join([trans for trans in transitions]))

    # create graph 
    ts_i = graphviz.Digraph('finite_state_machine', filename='asm1_i.gv', format='png')
    ts_i.attr(rankdir='LR')
    start = str('[1.free]')

    ts_i.attr('node', shape='point')
    ts_i.node('start')
    ts_i.attr('node', shape='circle', penwidth='6.0', fontname='Sans Not-Rotated 20', fontsize='20')
    ts_i.attr('edge', penwidth='3.0', fontname='Sans Not-Rotated 20', fontsize='20')
    ts_i.edge('start', start)

    # adding edges to the graph
    for edge in firing_rules:
        source = '[' + ", ".join([edge[0][i] for i in range(len(edge[0]))]) + ']'
        dest = '[' + ", ".join([edge[2][i] for i in range(len(edge[2]))]) + ']'
        name = str(edge[1][0])
        ts_i.edge(source, dest, name)

    root_folder = os.path.dirname(os.path.abspath(__file__))

    # Visualize the transition system
    ts_i.render(os.path.join(root_folder, "test-visualize", "asm1b", "asm1b_i"), view=True)