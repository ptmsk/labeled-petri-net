from os import sep
from typing_extensions import Concatenate

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
        :places: Places in petri net
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
        Return all transition relations in the net
        """
        print("Initial marking: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", sep="")

        markings_set = set()    # use to check whether loop contains in the net
        markings_set.add(tuple(p._holding for p in self._places))
        transition_relations = set()    

        while any(transition.fireable() for transition in self._transitions):
            concurrent_trans = []   # all fireable transitions index

            print("[", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", end="  ", sep="")
            
            s1 = [p._holding for p in self._places]
            s2 = []
            for i in range(self._n_transitions):
                if self._transitions[i].fireable():
                    concurrent_trans.append(i)
                    s2.append(self._transitions[i]._name)

            # fire concurrently
            for i in concurrent_trans:
                self._transitions[i].fire()

            print("[", ", ".join(["{0}".format(self._transitions[i]._name) for i in concurrent_trans]), ">", 
                            "  [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", sep="")
            
            s3 = [p._holding for p in self._places]
            transition_relations.add(tuple([tuple(s1), tuple(s2), tuple(s3)]))
            
            # check whether contains loop in the nets
            old_size = markings_set.__len__()
            markings_set.add(tuple(s3))
            if old_size == markings_set.__len__():
                print("Loop detected! Terminate firing!")
                print("\nEnd firing: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", sep="")
                return transition_relations
            
        print("\nEnd firing: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", sep="")
        return transition_relations

    def run_sequent_rec(self, transition_indices, trans_relations):
        """ 
        Fire all available transitions sequentially in the net until none left
        transition_indices: all fireable transitions
        trans_relations: all transition relations in the net
        """
        for idx in transition_indices:
            reserve_markings = [p._holding for p in self._places]   # reserve markings for recursion
            
            s1 = [p._holding for p in self._places]
            s2 = [self._transitions[idx]._name] 

            print("[", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", end="  ", sep="")
            self._transitions[idx].fire()
            print("[", self._transitions[idx]._name, ">", 
                    "  [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", sep="")

            s3 = [p._holding for p in self._places]

            old_size = trans_relations.__len__()
            trans_relations.add(tuple([tuple(s1), tuple(s2), tuple(s3)]))
            if old_size == trans_relations.__len__():
                return

            fireable_trans = []
            for i in range(self._n_transitions):
                if self._transitions[i].fireable():
                    fireable_trans.append(i)
            
            for i in fireable_trans:
                self.run_sequent_rec([i], trans_relations)

            # restore markings
            self.set_markings(reserve_markings)
            
        if not(any(transition.fireable() for transition in self._transitions)):
            return
        
    def run_sequent(self):
        """ 
        Fire all available transitions sequentially in the net until none left
        Return all transition relations in the net
        """
        fireable_trans = []
        for i in range(self._n_transitions):
            if self._transitions[i].fireable():
                fireable_trans.append(i)
        trans_relations = set()
        self.run_sequent_rec(fireable_trans, trans_relations)
        return trans_relations

    def result_firing_one(self):
        if self._n_transitions == 0:
            print ("Empty petri net!")
            return
        print("Initial marking: [", ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places]), "]", sep="")
        initial_marking = [place._holding for place in self._places]
        check_exist_marking = False
        for ts in self._transitions:
            enabled = ts.fire()
            if enabled:
                print("(N, M0) [{0}> (N, [{1}])".format(ts._name, ", ".join(["{0}.{1}".format(p._holding, p._name) for p in self._places])))
                check_exist_marking = True
                self.set_markings(initial_marking)
        if check_exist_marking == False:
            print("No reachable marking exists!")

def testPNA():
    place_names = ["wait", "inside", "done"]
    print("please enter the number of tokens in place 'wait', 'inside', 'done', respectively: ")
    place_holding = [int(input()) for _ in range(3)]
    place = list(zip(place_names, place_holding))

    obj_place = [Place(*p) for p in place]

    start = Transition("start", InArc(obj_place[0]), OutArc(obj_place[1]))
    change = Transition("change", InArc(obj_place[1]), OutArc(obj_place[2]))
    
    petri_net = PetriNet([start, change], obj_place) # or PetriNet([start, change])
    petri_net.run_concurrent()
    petri_net.set_markings([2, 1, 1])
    trans_relation = petri_net.run_sequent()
    for trans in trans_relation:
        print(trans)

def testPS():
    place_names = ['free', 'busy', 'docu']
    print("please enter the number of tokens in place 'free', 'busy', 'docu', respectively: ")
    place_holding = [int(input()) for _ in range(3)]
    place = list(zip(place_names, place_holding))

    obj_place = [Place(*p) for p in place]

    start = Transition('start', InArc(obj_place[0]), OutArc(obj_place[1]))
    change = Transition("change", InArc(obj_place[1]), OutArc(obj_place[2]))
    end = Transition("end", InArc(obj_place[2]), OutArc(obj_place[0]))

    petri_net = PetriNet([start, change, end], obj_place)
    petri_net.run_concurrent()
    petri_net.set_markings([1, 0, 0])
    trans_relation = petri_net.run_sequent()
    for trans in trans_relation:
        print(trans)
        
if __name__ == "__main__":
    place_names = ["wait", "inside", "done"]
    print("please enter the number of tokens in place 'wait', 'inside', 'done', respectively: ")
    place_holding = [int(input()) for _ in range(3)]
    place = list(zip(place_names, place_holding))

    obj_place = [Place(*p) for p in place]

    start = Transition("start", InArc(obj_place[0]), OutArc(obj_place[1]))
    change = Transition("change", InArc(obj_place[1]), OutArc(obj_place[2]))
    
    petri_net = PetriNet([start, change], obj_place) # or PetriNet([start, change])

    petri_net.result_firing_one()