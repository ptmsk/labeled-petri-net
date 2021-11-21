import net2 as ptn
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
petri_net = ptn.PetriNet(transitions, dict(places))

""" ---------- 1.b (ii) ---------- """
# Create transition system from the net above with maximum 2 tokens at each place
print("\n1.b.(ii): Create transition system from the net above with maximum 2 tokens at each place and maximum 1 token at [busy]\n")
max_token = 2
# set max_token
for p in petri_net._places.values():
    p._max_token = max_token

init_marking = [2, 0, 0]
print("Initial marking: [2.free]\n")
petri_net.set_markings(init_marking)

# set max_token in place: [busy]
petri_net._places['busy']._max_token = 1

# find all riring rules:
firing_rules = list(petri_net.run_sequent())

# find all markings at states and all transitions in the new transition
states = set()
transitions = set()
print("All riring rules: ")
for trans in firing_rules:
    states.add("[" + ", ".join([trans[0][i] for i in range(len(trans[0]))]) + "]")
    states.add("[" + ", ".join([trans[2][i] for i in range(len(trans[2]))]) + "]")
    transitions.add(trans[1][0])
    print("[", ", ".join([trans[0][i] for i in range(len(trans[0]))]), "]", end="  ", sep="")
    print("[", trans[1][0], ">", "  [", ", ".join([trans[2][i] for i in range(len(trans[2]))]), "]", sep="")

print("All states: ", "; ".join([st for st in states]))
print("All transitions: ", "; ".join([trans for trans in transitions]))

# create graph 
ts_ii = graphviz.Digraph('finite_state_machine', filename='asm1_ii.gv', format='png')
start = str('[2.free]')

ts_ii.attr(rankdir='LR')
ts_ii.attr('node', shape='point')
ts_ii.node('start')
ts_ii.attr('node', shape='circle', height='2.2', penwidth='6.0', fontname='Sans Not-Rotated 20', fontsize='20')
ts_ii.attr('edge', penwidth='3.0', fontname='Sans Not-Rotated 20', fontsize='20')
ts_ii.edge('start', start)

# adding edges to the graph
for edge in firing_rules:
    source = '[' + ", ".join([edge[0][i] for i in range(len(edge[0]))]) + ']'
    dest = '[' + ", ".join([edge[2][i] for i in range(len(edge[2]))]) + ']'
    name = str(edge[1][0])
    ts_ii.edge(source, dest, name, penwidth='3.0')

ts_ii.view()