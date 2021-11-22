import net as ptn


def __add__ (self : ptn.PetriNet, other : ptn.PetriNet):
    """
    Operator overloading used to merge 2 petri net
    """
    if len(self._transitions) == 0:
        return other
    elif len(other._transitions) == 0:
        return self
    m_places = self._places
    m_transitions = self._transitions

    for ts in other._transitions:
        appear = False
        if ts in m_transitions.keys():
            appear = True
        else:
            m_transitions[ts] = other._transitions[ts]
        for inplace in other._transitions[ts]._inarcs:
            if inplace in m_places.keys():
                other._transitions[ts]._inarcs[inplace] = ptn.InArc(m_places[inplace])
            else:
                m_places[inplace] = other._transitions[ts]._inarcs[inplace]._place
        for outplace in other._transitions[ts]._outarcs:
            if outplace in m_places.keys():
                other._transitions[ts]._outarcs[outplace] = ptn.OutArc(m_places[outplace])
            else:
                m_places[outplace] = other._transitions[ts]._outarcs[outplace]._place
        if appear:
            m_transitions[ts]._inarcs.update(other._transitions[ts]._inarcs)
            m_transitions[ts]._outarcs.update(other._transitions[ts]._outarcs)
    #end
    m_net = ptn.PetriNet(m_transitions, m_places)
    return m_net

setattr(ptn.PetriNet, "__add__", __add__)

# create s_places for specialist
s_place_names = ["free", "busy", "docu"]
s_places_obj = [ptn.Place() for i in range(len(s_place_names))]
s_places = list(zip(s_place_names, s_places_obj))


# create transitions
s_transition = dict(
    start = ptn.Transition(s_places, [0], [1]),
    change = ptn.Transition(s_places, [1], [2]),
    end = ptn.Transition(s_places, [2], [0]),
)

# create the net for specialist
s_net = ptn.PetriNet(s_transition, dict(s_places))

# create s_places for patients
p_place_names = ["wait", "inside", "done"]
p_places_obj = [ptn.Place() for i in range(len(p_place_names))]
p_places = list(zip(p_place_names, p_places_obj))

# create transitions
p_transition = dict(
    start = ptn.Transition(p_places, [0], [1]),
    change = ptn.Transition(p_places, [1], [2]),
)

# create the net for patients
p_net = ptn.PetriNet(p_transition, dict(p_places))
m_net = s_net + p_net

if __name__ == "__main__":
    m_net.draw("m_net", "asm3")
    m_net.run_debug("m_net_run", "asm3")