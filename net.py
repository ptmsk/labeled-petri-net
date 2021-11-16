class Place:
    def __init__(self, name, holding=0):
        """
        Place object in Petri Net
        :name: Name of place.
        :holding: The total tokens in place.
        """
        self._name = name
        self._holding = holding
    

class ArcBase:
    def __init__(self, place, weight=1):
        """
        Arc object in Petri Net connecting place and transition.
        :place: Input/ output place.
        :weight: Number of tokens added/removed to/from the place.
        """
        self._place = place
        self._weight = weight


class OutArc(ArcBase):
    def __init__(self, place, weight=1):
        """
        Directed arc from transition to output place.
        :place: Output place.
        :weight: Number of tokens added to place.
        """
        super().__init__(place, weight)
    
    def produce(self):
        """
        Produce tokens in output places
        """
        self._place._holding += self._weight


class InArc(ArcBase):
    def __init__(self, place, weight=1):
        """
         Directed arc from input place to transition.
        :place: Input place.
        :weight: Number of tokens removed from place.
        """
        super().__init__(place, weight)

    def enabled(self):
        """
        Check if the trasition is enabled
        """
        return self._place._holding >= self._weight

    def consume(self):
        """
        Consume tokens from input places
        """
        self._place._holding -= self._weight


class Transition:
    def __init__(self, name, inarcs, outarcs):
        """
        Transition object in Petri Net.
        :name: Name of trasition.
        :inarcs: One or List of input arcs connect to the transition.
        :outarcs: One or List of output arcs connect to the transition.
        """
        if not(isinstance(inarcs, list)):
            inarcs = [inarcs]
        if not(isinstance(outarcs, list)):
            outarcs = [outarcs]
        self._name = name
        self._inarcs = set(inarcs)
        self._outarcs = set(outarcs)

    def fire(self):
        """
        Apply firing rule
        """
        # Check if the trasition is enabled.
        enabled = all(inarc.enabled() for inarc in self._inarcs)

        if enabled:
            for arc in self._inarcs:
                arc.consume()
            for arc in self._outarcs:
                arc.produce()
        return enabled

    
class PetriNet:
    def __init__(self, *transitions):
        """
        Petri Net object.
        :transition: The transitions (which include the places in arc).
        """
        self._transitions = transitions

    def fsgenerate(self):
        """
        Firing sequence generator.
        """
        transitions_name = (ts._name for ts in self._transitions)
        print("Enter a firing sequence", tuple(["{0} for '{1}'".format(*i) for i in enumerate(transitions_name)]), ":")
        fs = input()
        # Ex: fs = "0 0 1 1 0 2 1"
        return list(map(int, map(str.strip, fs.split())))

    def run(self, pt):
        """
        Activate firing sequence.
        :pt: list of places with tokens.
        """
        firing_sequence = petri_net.fsgenerate()
        print("Using firing sequence:\n" + " => ".join([self._transitions[i]._name for i in firing_sequence]))
        print("Initial marking: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in pt]), "]")

        for i in firing_sequence:
            if self._transitions[i].fire():
                print("'{}' fired...".format(self._transitions[i]._name))
                print("\t ===>    [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in pt]), "]")
            else:
                print("'{}' is not enabled...".format(self._transitions[i]._name))
        
        print("\nEnd firing: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in pt]), "]")

    def run_debug(self, pt):
        """
        Apply firing sequence with debug mode.
        :pt: list of places with tokens.
        """
        print("Initial marking: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in pt]), "]")
        transitions_name = (ts._name for ts in self._transitions)
        choose_transition = "Choose a firing transition (" + ", ".join(["{0} for '{1}'".format(*i) for i in enumerate(transitions_name)]) +  ", -1 to finish firing): "
        i = int(input(choose_transition).strip())

        while i != -1:
            if self._transitions[i].fire():
                print("'{}' fired...".format(self._transitions[i]._name))
                print("\t ===>    [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in pt]), "]")
            else:
                print("'{}' is not enabled...".format(self._transitions[i]._name))
            i = int(input(choose_transition).strip())

        print("\nEnd firing: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in pt]), "]")

if __name__ == "__main__":
    place_names = ["wait", "inside", "done"]
    print("please enter the number of tokens in place 'wait', 'inside', 'done', respectively: ")
    place_holding = [int(input()) for _ in range(3)]
    place = list(zip(place_names, place_holding))

    obj_place = [Place(*p) for p in place]

    start = Transition("start", InArc(obj_place[0]), OutArc(obj_place[1]))
    change = Transition("change", InArc(obj_place[1]), OutArc(obj_place[2]))

    petri_net = PetriNet(start, change) # or PetriNet([start, change])
    petri_net.run_debug(obj_place)