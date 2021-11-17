import net as ptn

""" Create specialist petri net """
# create places
place_names = ["free", "busy", "docu"]
places = [ptn.Place(p) for p in place_names]

# create transitions
start = ptn.Transition("start", ptn.InArc(places[0]), ptn.OutArc(places[1]))
change = ptn.Transition("change", ptn.InArc(places[1]), ptn.OutArc(places[2]))
end = ptn.Transition("end", ptn.InArc(places[2]), ptn.OutArc(places[0]))

# create the net
petri_net = ptn.PetriNet([start, change, end], places)

""" ---------- 1.b (i) ---------- """
# Create transition system from the net above with maximum 1 tokens at each place
max_token = 1
# set max_token
for p in petri_net._places:
    p._max_token = max_token

init_marking = [1, 0 , 0]
petri_net.set_markings(init_marking)

# find all transition relations:
trans_relations = petri_net.run_sequent()

# find all markings at states and all transitions in the new transition
states = set()
transitions = set()
for trans in trans_relations:
    states.add(trans[0])
    states.add(trans[2])
    transitions.add(trans[1])


""" ---------- 1.b (ii) ---------- """
# Create transition system from the net above with maximum 1 tokens at each place
max_token = 2
# set max_token
for p in petri_net._places:
    p._max_token = max_token

init_marking = [2, 0 , 0]
petri_net.set_markings(init_marking)

# set max_token in place: [busy]
petri_net._places[1]._max_token = 1

# find all transition relations:
trans_relations = petri_net.run_sequent()

# find all markings at states and all transitions in the new transition
states = set()
transitions = set()
for trans in trans_relations:
    states.add(trans[0])
    states.add(trans[2])
    transitions.add(trans[1])