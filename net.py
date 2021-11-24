"""
A Petri net simple implementation
"""
import os
import shutil
import graphviz

class Place:
    def __init__(self, holding=0, max_token=-1):
        """
        Place object in Petri Net
        :holding: The total tokens in place.
        :max_token: The maximum token place can store.
        """
        if max_token != -1 and max_token < holding:
            print("Warning: Place hold too many tokens! Set holding to max_token")
            self._holding = max_token
            self._max_token = max_token
            return
        self._holding = holding
        self._max_token = max_token
    
    def receivable(self, tokens=1) -> bool:
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

    def enabled(self) -> bool:
        """
        Check whether the outarc of the transition is enabled
        """
        return self._place.receivable()

    def produce(self) -> None:
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

    def enabled(self) -> bool:
        """
        Check if the inarc of the trasition is enabled
        """
        return self._place._holding >= self._weight

    def consume(self) -> None:
        """
        Consume tokens from input places
        """
        if self.enabled():
            self._place._holding -= self._weight


class Transition:
    def __init__(self, places: list, inarc_indices: list, outarcs_indices: list):
        """
        Transitions in petri net
        :places: place objects
        :inarc_indices: map places' name with its input arc contain the place object
        :outarc_indices: map places' name with its output arc contain the place object
        """
        self._inarcs = dict([(places[i][0], InArc(places[i][1])) for i in inarc_indices])
        self._outarcs = dict([(places[i][0], OutArc(places[i][1])) for i in outarcs_indices])

    def fireable(self) -> bool:
        """"
        Check whether the transition is fireable
        """
        return (all(inarc.enabled() for inarc in self._inarcs.values())
                and any(outarc.enabled() for outarc in self._outarcs.values()))

    def fire(self) -> bool:
        """
        Apply firing rule
        """
        # Check if the trasition is enabled.
        enabled = self.fireable()

        if enabled:
            for arc in self._inarcs.values():
                arc.consume()
            for arc in self._outarcs.values():
                arc.produce()
        return enabled

    
class PetriNet:
    def __init__(self, transitions: dict, places: dict):
        """
        Petri Net object.
        :transition: The transitions (which include the places in arc).
        :places: places in petri net
        """
        self._transitions = transitions
        self._places = places
    
    def set_markings(self, markings: list) -> None:
        """
        Set petri net with given markings
        :markings: list of markings sequentially
        """
        for i, key in enumerate(self._places):
            if (self._places[key]._max_token != -1 and self._places[key]._max_token < markings[i]):
                print("Warning: Place '{0}' can't receive more tokens than {1}. Set new token to max_token".format(key, self._places[key]._max_token))
                self._places[key]._holding = self._places[key]._max_token
                continue
            self._places[key]._holding = markings[i]

    def fsgenerate(self) -> list:
        """
        Firing sequence generator.
        """
        map_key = dict(enumerate(self._transitions.keys()))
        print("Enter a firing sequence", tuple(["{0} for {1}".format(*i) for i in map_key.items()]), ":")
        fs = input()
        # Ex: fs = "0 0 1 1 0 2 1"
        fs = list(map(int, map(str.strip, fs.split())))
        return list(map_key[i] for i in fs)

    def run(self) -> None:
        """
        Activate firing sequence.
        :firing_sequence: Sequence of firing transitions.
        """
        firing_sequence = self.fsgenerate()
        print("Using firing sequence:\n" + " => ".join(firing_sequence))
        print("Initial marking: [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "]")

        for key in firing_sequence:
            if self._transitions[key].fire():
                print("'{}' fired...".format(key))
                print("\t ===>    [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "]", sep="")
            else:
                print("'{}' is not enabled...".format(key))
        
        print("\nEnd firing: [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "]", sep="")

    def run_debug(self, name="run_debug", folder="visualize"):
        """
        Apply firing sequence with debug mode and visualize option.
        :name: Name of the petri net
        :folder: Folder to store visualization
        """
        root_folder = os.path.dirname(os.path.abspath(__file__))
        visual_path = os.path.join(root_folder, "test-visualize")
        if os.path.exists(visual_path):
            old_folder_path = os.path.join(visual_path, folder)
            if os.path.exists(old_folder_path):
                shutil.rmtree(old_folder_path)
        self.draw(name, folder)
        map_key = dict(enumerate(self._transitions.keys()))
        print("Initial marking: [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "]", sep="")
        if not(any(transition.fireable() for transition in self._transitions.values())):
            print("No enabled transition found!")
            return
        choose_transition = ("Choose a firing transition (" + ", ".join(["{0} for '{1}'".format(*i) for i in map_key.items()])
                             +  ", {} to visualize, -1 to finish firing): ".format(len(self._transitions)))
        i = int(input(choose_transition).strip())
        count = 0
        name += "_run"
        while i != -1:
            if i == len(self._transitions):
                if count == 0:
                    self.draw(name, folder)
                else:
                    self.draw("_".join([name, str(count)]), folder)
                count += 1
                i = int(input(choose_transition).strip())
                continue
            key = map_key[i]
            if self._transitions[key].fire():
                print("'{}' fired...".format(key))
                print("\t ===>    [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "]", sep="")
            else:
                print("'{}' is not enabled...".format(key))
            if not(any(transition.fireable() for transition in self._transitions.values())):
                print("No more enabled transitions! Stop firing.")
                v = input("Press 1 to visualize the final transition, else press 0: ")
                if v == "1":
                    name = name[:-3] + "final"
                    self.draw(name, folder)
                break
            i = int(input(choose_transition).strip())

        print("\nEnd firing: [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "]", sep="")

    def run_concurrent(self) -> set:
        """
        Fire all available transitions concurrently in the net until none left
        Return all firing rules in the net
        """
        print("Initial marking: [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "]")

        markings_set = set()    # use to check whether loop contains in the net
        markings_set.add(tuple(p._holding for p in self._places.values()))
        firing_rules = set()    

        while any(transition.fireable() for transition in self._transitions.values()):

            print("(N, [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "])", end="  ", sep="")
            
            s1 = []
            for p in self._places.items():
                if p[1]._holding != 0:
                    s1.append(str(p[1]._holding) + "." + p[0])
                
            s2 = []
            for key in self._transitions:
                if self._transitions[key].fireable():
                    s2.append(key)

            # fire concurrently
            for i in s2:
                self._transitions[i].fire()

            print("[", ", ".join(s2), ">", 
                  "  (N, [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "])", sep="")
            
            s3 = []
            for p in self._places.items():
                if p[1]._holding != 0:
                    s3.append(str(p[1]._holding) + "." + p[0])
            firing_rules.add(tuple([tuple(s1), tuple(s2), tuple(s3)]))
            
            # check whether contains loop in the nets
            old_size = markings_set.__len__()
            markings_set.add(tuple([p._holding for p in self._places.values()]))
            if old_size == markings_set.__len__():
                print("Loop detected! Terminate firing!")
                print("\nEnd firing: [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "]", sep="")
                return firing_rules
            
        print("\nEnd firing: [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "]", sep="")
        return firing_rules

    def run_sequent_rec(self, transition_keys, firing_rules) -> None:
        """ 
        Fire all available transitions sequentially in the net until none left
        :transition_keys: all fireable transitions
        :firing_rules: all firing rules in the net
        """
        for key in transition_keys:
            reserve_markings = [p._holding for p in self._places.values()]   # reserve markings for recursion
            
            s1 = []
            for p in self._places.items():
                if p[1]._holding != 0:
                    s1.append(str(p[1]._holding) + "." + p[0])
        
            s2 = [key]
            # fire
            self._transitions[key].fire()

            s3 = []
            for p in self._places.items():
                if p[1]._holding != 0:
                    s3.append(str(p[1]._holding) + "." + p[0])

            old_size = firing_rules.__len__()
            firing_rules.add(tuple([tuple(s1), tuple(s2), tuple(s3)]))
            if old_size == firing_rules.__len__():
                return

            fireable_trans = []
            for key in self._transitions:
                if self._transitions[key].fireable():
                    fireable_trans.append(key)
            
            for key in fireable_trans:
                self.run_sequent_rec([key], firing_rules)

            # restore markings
            self.set_markings(reserve_markings)
            
        if not(any(transition.fireable() for transition in self._transitions.values())):
            return
        
    def run_sequent(self) -> set:
        """ 
        Fire all available transitions sequentially in the net until none left
        Return all firing rules in the net
        """
        fireable_trans = []
        for key in self._transitions:
            if self._transitions[key].fireable():
                fireable_trans.append(key)
        firing_rules = set()
        self.run_sequent_rec(fireable_trans, firing_rules)
        return firing_rules

    def draw(self, name="petri_net", folder="visualize") -> None:
        """
        Use graphviz to visualize petri net
        :name: Name of the visualization
        :folder: Folder containing visualization petri net
        """
        ptn = graphviz.Digraph(name, format="png")
        ptn.attr(rankdir='LR')
        ptn.attr('node', shape='circle', height='1.5', penwidth='3.0', fontname='Sans Not-Rotated 20', fontsize='20')
        for place in self._places.items():
            place_with_tokens = place[0] + "\n" + str(place[1]._holding)
            ptn.node(place_with_tokens)
        ptn.attr('node', shape='box', height='1.5', penwidth='3.0', fontname='Sans Not-Rotated 20', fontsize='20')
        for transition in self._transitions.items():
            ptn.node(transition[0])
            for place_name in transition[1]._inarcs:
                place_with_tokens = place_name + "\n" + str(self._places[place_name]._holding)
                ptn.edge(place_with_tokens, transition[0], penwidth='3.0')
            for place_name in transition[1]._outarcs:
                place_with_tokens = place_name + "\n" + str(self._places[place_name]._holding)
                ptn.edge(transition[0], place_with_tokens, penwidth='3.0')
        root_folder = os.path.dirname(os.path.abspath(__file__))
        ptn.render(os.path.join(root_folder, "test-visualize", folder, name), view=True)
        print("Petri net visualized!...")

    def detail_Print(self, nname = "a"):
        """
        Print the details of a petri net
        :nname: Name of the petri net
        """
        print('---------------------------------------------------')
        print("This is details of", nname ,"petri net!")
        print("Denote petri net N as quadruple: N = (P, T, F, M0)")
        print("Where:")
        print("Places P = {", ", ".join(self._places), "}", sep="")
        print("Transitions T = {", ", ".join(self._transitions), "}", sep="")
        iF = []
        oF = []
        for ts in self._transitions.items():
            iF.extend("({0}, {1})".format(arc, ts[0]) for arc in ts[1]._inarcs)
            oF.extend("({0}, {1})".format(ts[0], arc) for arc in ts[1]._outarcs)
        print("Flows F = IF X OF = {", ", ".join(iF),"}\n\t\t  X {", ", ".join(oF), "}", sep="")

        print("Initial marking M0 = [", ", ".join("{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()), "]", sep="")
        print('---------------------------------------------------')

    def __add__ (self, other):
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
                    other._transitions[ts]._inarcs[inplace] = InArc(m_places[inplace])
                else:
                    m_places[inplace] = other._transitions[ts]._inarcs[inplace]._place
            for outplace in other._transitions[ts]._outarcs:
                if outplace in m_places.keys():
                    other._transitions[ts]._outarcs[outplace] = OutArc(m_places[outplace])
                else:
                    m_places[outplace] = other._transitions[ts]._outarcs[outplace]._place
            if appear:
                m_transitions[ts]._inarcs.update(other._transitions[ts]._inarcs)
                m_transitions[ts]._outarcs.update(other._transitions[ts]._outarcs)
        
        # construct new petri net
        m_net = PetriNet(m_transitions, m_places)
        return m_net

    def result_firing_one(self):
        """
        Reachable marking by firing once.
        """
        if self._transitions.__len__() == 0 and self._places.__len__() == 0:
            print ("Empty petri net!")
            return
        print("Initial marking M0: [", ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()]), "]", sep="")
        root_folder = os.path.dirname(os.path.abspath(__file__))
        visual_path = os.path.join(root_folder, "test-visualize")
        if os.path.exists(visual_path):
            old_folder_path = os.path.join(visual_path, "asm4")
            if os.path.exists(old_folder_path):
                shutil.rmtree(old_folder_path)
        self.draw("initial_marking", "asm4")
        initial_marking = [place._holding for place in self._places.values()]
        check_exist_marking = False
        for ts in self._transitions.items():
            enabled = ts[1].fire()
            if enabled:
                print("(N, M0) [{0}> (N, [{1}])".format(ts[0], ", ".join(["{0}.{1}".format(p[1]._holding, p[0]) for p in self._places.items()])))
                check_exist_marking = True
                self.draw("transition_{}".format(ts[0]), "asm4")
                self.set_markings(initial_marking)
        if check_exist_marking == False:
            print("No reachable marking exists!")

if __name__ == "__main__":
    print("this is net.py")