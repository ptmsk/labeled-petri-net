"""
A Petri net simple implementation
"""

import graphviz

class Place:
    def __init__(self, name, holding=0, max_token=-1):
        """
        Place object in Petri Net
        :name: Name of place.
        :holding: The total tokens in place.
        """
        self._name = name
        self._holding = holding
        self._max_token = max_token
    
    def receivable(self, tokens=1):
        """
        Check whether place can receive more tokens
        tokens: number of tokens received
        """
        return (self._max_token == -1 or self._holding + tokens <= self._max_token)

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

    def enabled(self):
        """
        Check whether the outarc of the transition is enabled
        """
        return self._place.receivable()

    def produce(self):
        """
        Produce tokens in output places
        """
        if self.enabled():
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
        Check if the inarc of the trasition is enabled
        """
        return self._place._holding >= self._weight

    def consume(self):
        """
        Consume tokens from input places
        """
        if self.enabled():
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

    def fireable(self):
        """"
        Check whether the transition is fireable
        """
        return (all(inarc.enabled() for inarc in self._inarcs)
                and any(outarc.enabled() for outarc in self._outarcs))

    def fire(self):
        """
        Apply firing rule
        """
        # Check if the trasition is enabled.
        enabled = self.fireable()

        if enabled:
            for arc in self._inarcs:
                arc.consume()
            for arc in self._outarcs:
                arc.produce()
        return enabled

    
class PetriNet:
    def __init__(self, transitions, places):
        """
        Petri Net object.
        :transition: The transitions (which include the places in arc).
        """
        self._transitions = transitions
        self._places = places
        self._n_transitions = len(transitions)
    
    def set_markings(self, markings):
        for i in range(len(markings)):
            self._places[i]._holding = markings[i]

    def run_concurrent(self):
        """
        Fire all available transitions concurrently in the net until none left
        Return all firing rules in the net
        """
        print("Initial marking: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]")

        markings_set = set()    # use to check whether loop contains in the net
        markings_set.add(tuple(p._holding for p in self._places))
        firing_rules = set()    

        while any(transition.fireable() for transition in self._transitions):
            concurrent_trans = []   # all fireable transitions index

            print("(N, [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "])", end="  ", sep="")
            
            s1 = []
            for p in self._places:
                if p._holding != 0:
                    s1.append(str(p._holding) + "." + p._name)
                
            s2 = []
            for i in range(self._n_transitions):
                if self._transitions[i].fireable():
                    concurrent_trans.append(i)
                    s2.append(self._transitions[i]._name)

            # fire concurrently
            for i in concurrent_trans:
                self._transitions[i].fire()

            print("[", ", ".join(["{0}".format(self._transitions[i]._name) for i in concurrent_trans]), ">", 
                            "  (N, [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "])", sep="")
            
            s3 = []
            for p in self._places:
                if p._holding != 0:
                    s3.append(str(p._holding) + "." + p._name)
            firing_rules.add(tuple([tuple(s1), tuple(s2), tuple(s3)]))
            
            # check whether contains loop in the nets
            old_size = markings_set.__len__()
            markings_set.add(tuple([p._holding for p in self._places]))
            if old_size == markings_set.__len__():
                print("Loop detected! Terminate firing!")
                print("\nEnd firing: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", sep="")
                return firing_rules
            
        print("\nEnd firing: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", sep="")
        return firing_rules

    def run_sequent_rec(self, transition_indices, firing_rules):
        """ 
        Fire all available transitions sequentially in the net until none left
        transition_indices: all fireable transitions
        firing_rules: all firing rules in the net
        """
        for idx in transition_indices:
            reserve_markings = [p._holding for p in self._places]   # reserve markings for recursion
            
            s1 = []
            for p in self._places:
                if p._holding != 0:
                    s1.append(str(p._holding) + "." + p._name)
        
            s2 = [self._transitions[idx]._name] 
            # fire
            self._transitions[idx].fire()

            s3 = []
            for p in self._places:
                if p._holding != 0:
                    s3.append(str(p._holding) + "." + p._name)

            old_size = firing_rules.__len__()
            firing_rules.add(tuple([tuple(s1), tuple(s2), tuple(s3)]))
            if old_size == firing_rules.__len__():
                return

            fireable_trans = []
            for i in range(self._n_transitions):
                if self._transitions[i].fireable():
                    fireable_trans.append(i)
            
            for i in fireable_trans:
                self.run_sequent_rec([i], firing_rules)

            # restore markings
            self.set_markings(reserve_markings)
            
        if not(any(transition.fireable() for transition in self._transitions)):
            return
        
    def run_sequent(self):
        """ 
        Fire all available transitions sequentially in the net until none left
        Return all firing rules in the net
        """
        fireable_trans = []
        for i in range(self._n_transitions):
            if self._transitions[i].fireable():
                fireable_trans.append(i)
        firing_rules = set()
        self.run_sequent_rec(fireable_trans, firing_rules)
        return firing_rules

    def result_firing_one(self):
        """
        Reachable marking by firing once.
        """
        if self._n_transitions == 0:
            print ("Empty petri net!")
            return
        print("Initial marking M0: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", sep="")
        initial_marking = [place._holding for place in self._places]
        check_exist_marking = False
        for ts in self._transitions:
            enabled = ts.fire()
            if enabled:
                print("(N, M0) [{0}> (N, [{1}])".format(ts._name, ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places])))
                check_exist_marking = True
                # ptn = self.draw("transition_{}".format(ts._name))
                # ptn.view()
                self.set_markings(initial_marking)
        if check_exist_marking == False:
            print("No reachable marking exists!")

    def draw(self, name="petri_net"):
        """
        Use graphviz to visualize petri net
        """
        ptn = graphviz.Digraph(name, format="png")
        ptn.attr(rankdir='LR')
        ptn.attr('node', shape='circle', height='2.2', penwidth='6.0', fontname='Sans Not-Rotated 20', fontsize='20')
        for place in self._places:
            place_with_tokens = place._name + "\n" + str(place._holding)
            ptn.node(place_with_tokens)
        ptn.attr('node', shape='box', height='2.2', penwidth='6.0', fontname='Sans Not-Rotated 20', fontsize='20')
        for transition in self._transitions:
            ptn.node(transition._name)
            for arc in transition._inarcs:
                place_with_tokens = arc._place._name + "\n" + str(arc._place._holding)
                ptn.edge(place_with_tokens, transition._name, penwidth='3.0')
            for arc in transition._outarcs:
                place_with_tokens = arc._place._name + "\n" + str(arc._place._holding)
                ptn.edge(transition._name, place_with_tokens, penwidth='3.0')
        # return ptn
        ptn.view()

if __name__ == "__main__":
    place_names = ["wait", "inside", "done"]
    print("please enter the number of tokens in place 'wait', 'inside', 'done', respectively: ")
    place_holding = [int(input()) for _ in range(3)]
    place = list(zip(place_names, place_holding))

    obj_place = [Place(*p) for p in place]

    start = Transition("start", InArc(obj_place[0]), OutArc(obj_place[1]))
    change = Transition("change", InArc(obj_place[1]), OutArc(obj_place[2]))

    petri_net = PetriNet([start, change], obj_place) # or PetriNet([start, change])
    # firing_rule = petri_net.run_sequent()
    # print(firing_rule)
    # print(len(firing_rule))
    # petri_net.result_firing_one()
    petri_net.draw()