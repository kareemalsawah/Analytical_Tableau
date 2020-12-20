class Variable():
    def __init__(self,inbound_vars=[]):
        self.inbound_vars = inbound_vars
        self.outbound_vars = []

        self.value = None
        self.expanded = False

        for n in self.inbound_vars:
            n.outbound_vars.append(self)
    
    def forward(self):
        raise NotImplemented
        
    def __str__(self):
        raise NotImplemented
    
    def __add__(self,other):
        return OR(self,other)
    
    def __mul__(self,other):
        return AND(self,other)
    
    def __rshift__(self,other):
        return IMPLICATION(self,other)
    
    def __invert__(self):
        return NOT(self)
        

class Input(Variable):
    def __init__(self,name):
        Variable.__init__(self)
        self.name = name
        self.expanded = False

    def forward(self,value=None):
        if value is not None:
            self.value = value
    def __str__(self):
        return self.name
    
class One(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.name = "1"
        self.value = 1
        self.expanded = False

    def forward(self):
        pass
    def __str__(self):
        return self.name
    
    
class Zero(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.name = "0"
        self.value = 0
        self.expanded = False

    def forward(self):
        pass
    
    def __str__(self):
        return self.name
            
class OR(Variable):
    def __init__(self,*inputs):
        Variable.__init__(self,inputs)
        self.expanded = False

    def forward(self):
        self.value = False
        for n in self.inbound_vars:
            if n.value is not None:
                self.value = self.value or n.value
    def __str__(self):
        to_print = ""
        for term in self.inbound_vars:
            if type(term) is not Input:
                to_print += "(" + str(term) + ")+"
            else:
                to_print += str(term)+"+"
        return to_print[:-1]

class AND(Variable):
    def __init__(self,*inputs):
        Variable.__init__(self,inputs)
        self.expanded = False

    def forward(self):
        self.value = True
        for n in self.inbound_vars:
            if n.value is not None:
                self.value = self.value and n.value
                
    def __str__(self):
        to_print = ""
        for term in self.inbound_vars:
            
            if type(term) is not Input:
                to_print += "(" + str(term) + ")*"
            else:
                to_print += str(term)+"*"
        return to_print[:-1]
                
class NOT(Variable):
    def __init__(self,*inputs):
        Variable.__init__(self,inputs)
        self.expanded = False

    def forward(self):
        self.value = False
        if len(self.inbound_vars)>1:
            print("Error, NOT gate can only take one input")
        else:
            self.value = not self.inbound_vars[0].value
            
    def __str__(self):
        if type(self.inbound_vars[0]) is Input:
            return "~"+str(self.inbound_vars[0])
        else:
            return "~("+str(self.inbound_vars[0])+")"
                
class IMPLICATION(Variable):
    def __init__(self,*inputs):
        Variable.__init__(self,inputs)
        self.expanded = False

    def forward(self):
        self.value = True
        if self.inbound_vars[0].value == 1 and self.inbound_vars[1].value == 0:
            self.value = False
                
    def __str__(self):
        to_print = str(self.inbound_vars[0])+"->"+str(self.inbound_vars[1])
        return to_print
    
class NOR(Variable):
    def __init__(self,*inputs):
        Variable.__init__(self,inputs)

    def forward(self):
        self.value = False
        for n in self.inbound_vars:
            if n.value is not None:
                self.value = self.value or n.value
        self.value = not self.value
     
    def __str__(self):
        to_print = ""
        for term in self.inbound_vars:
            to_print += str(term) + " nor "
        return to_print[:-1]
        
        
        
class NAND(Variable):
    def __init__(self,*inputs):
        Variable.__init__(self,inputs)

    def forward(self):
        self.value = True
        for n in self.inbound_vars:
            if n.value is not None:
                self.value = self.value and n.value
        self.value = not self.value
    
    def __str__(self):
        to_print = ""
        for term in self.inbound_vars:
            to_print += str(term) + " nand "
        return to_print[:-1]
                
                
def topological_sort(feed_dict):
    """
    Sort the nodes in topological order using Kahn's Algorithm.

    `feed_dict`: A dictionary where the key is a `Input` Node and the value is the respective value feed to that Node.

    Returns a list of sorted nodes.
    """

    input_nodes = [n for n in feed_dict.keys()]

    G = {}
    nodes = [n for n in input_nodes]
    while len(nodes) > 0:
        n = nodes.pop(0)
        if n not in G:
            G[n] = {'in': set(), 'out': set()}
        for m in n.outbound_vars:
            if m not in G:
                G[m] = {'in': set(), 'out': set()}
            G[n]['out'].add(m)
            G[m]['in'].add(n)
            nodes.append(m)

    L = []
    S = set(input_nodes)
    while len(S) > 0:
        n = S.pop()

        if isinstance(n, Input):
            n.value = feed_dict[n]

        L.append(n)
        for m in n.outbound_vars:
            G[n]['out'].remove(m)
            G[m]['in'].remove(n)
            # if no other incoming edges add to S
            if len(G[m]['in']) == 0:
                S.add(m)
    return L


def forward_pass(output_node, sorted_nodes):
    """
    Performs a forward pass through a list of sorted nodes.

    Arguments:

        `output_node`: A node in the graph, should be the output node (have no outgoing edges).
        `sorted_nodes`: A topologically sorted list of nodes.

    Returns the output Node's value
    """

    for n in sorted_nodes:
        n.forward()

    return output_node.value


def int_to_binary(num,min_num_zeros=-1):
    binary_arr = []
    while(num>0):
        if num%2==1:
            binary_arr.append(True)
        else:
            binary_arr.append(False)
        num = num//2
    while(len(binary_arr)<min_num_zeros):
        binary_arr.append(False)
    return list(reversed(binary_arr))

def binary_to_int(num):
    answer = 0
    multiplier = 1
    reversed_num = list(reversed(num))
    for i in reversed_num:
        if i:
            answer += multiplier
        multiplier *= 2
    return answer

def truth_table(output_node,variables):
    num_vars = len(variables)
    results = []
    for i in range(0,pow(2,num_vars)):
        result = []
        binary_num = int_to_binary(i,num_vars)
        feed_dict = {}
        for var,val in zip(variables,binary_num):
            feed_dict[var] = val
            result.append(val)
        graph = topological_sort(feed_dict)
        output = forward_pass(output_node, graph)
        result.append(output)
        results.append(result)
    return results

def binary_dist(var_1,var_2):
    dist = 0
    for v1,v2 in zip(var_1,var_2):
        if v1 != v2:
            dist += 1
    return dist

def simplify_two_vars(var_1,var_2):
    new_var = []
    for v1,v2 in zip(var_1,var_2):
        if v1 == v2:
            new_var.append(v1)
        else:
            new_var.append(-1)
    return new_var

def combine_lists(l1,l2):
    new_l = []
    for i in l1:
        if i not in new_l:
            new_l.append(i)
    for i in l2:
        if i not in new_l:
            new_l.append(i)
    new_l.sort()
    return new_l


def find_best_term(levels,term):
    for level in levels:
        for minterm in level:
            if term in minterm[1]:
                return minterm 
            
            
def minterm_to_vars(minterm,variables):
    answer = None
    for idx,i in enumerate(minterm):
        if i != -1:
            if i:
                if answer is None:
                    answer = variables[idx]
                else:
                    answer = answer*variables[idx]
            else:
                if answer is None:
                    answer = ~variables[idx]
                else:
                    answer = answer*~variables[idx]
    if answer is None:
        return One()
    return answer

def f_from_minterms(minterm_indices,variables):
    f = None
    for index in minterm_indices:
        new_minterm = minterm_to_vars(int_to_binary(index,len(variables)),variables)
        if f is None:
            f = new_minterm
        else:
            f = f + new_minterm
    return f
def k_map_f(output_node,variables):
    num_vars = len(variables)
    min_terms = []
    added_terms = []
    for i in range(0,pow(2,num_vars)):
        min_term = []
        binary_num = int_to_binary(i,num_vars)
        feed_dict = {}
        for var,val in zip(variables,binary_num):
            feed_dict[var] = val
            min_term.append(val)
        graph = topological_sort(feed_dict)
        output = forward_pass(output_node, graph)
        if output:
            min_terms.append([min_term,[binary_to_int(min_term)]])
            added_terms.append(binary_to_int(min_term))
    
    terms_to_add = added_terms.copy()
    levels_of_minterms = [min_terms]
    for i in range(0,num_vars+1):
        current_level = []
        if len(levels_of_minterms[i]) == 0:
            break
        for idx,min_term in enumerate(levels_of_minterms[i]):
            for idx_2,min_term_2 in enumerate(levels_of_minterms[i]):
                if idx != idx_2:
                    if binary_dist(min_term[0],min_term_2[0]) == 1:
                        combined_terms = combine_lists(min_term[1],min_term_2[1])
                        if combined_terms not in added_terms:
                            current_level.append([simplify_two_vars(min_term[0],min_term_2[0]),combined_terms])
                            added_terms.append(combined_terms)
        levels_of_minterms.append(current_level)
    levels_of_minterms = list(reversed(levels_of_minterms[:-1]))
    best_terms = []
    terms_added = []
    for term in terms_to_add:
        if term not in terms_added:
            best_term = find_best_term(levels_of_minterms,term)
            best_terms.append(best_term)
            for term in best_term[1]:
                if term not in terms_added:
                    terms_added.append(term)
    new_variables = []
    for var in variables:
        new_variables.append(Input(var.name))
    
    answer = None
    for term in best_terms:
        minterm = minterm_to_vars(term[0],new_variables)
        if answer is None:
            answer = minterm
        else:
            answer = answer + minterm
        
    return answer


def k_map_truth_table(truth_table,variables):
    num_vars = len(variables)
    min_terms = []
    added_terms = []
    for i in range(0,pow(2,num_vars)):
        min_term = []
        binary_num = int_to_binary(i,num_vars)
        feed_dict = {}
        for var,val in zip(variables,binary_num):
            feed_dict[var] = val
            min_term.append(val)
        output = truth_table[i][-1]
        if output:
            min_terms.append([min_term,[binary_to_int(min_term)]])
            added_terms.append(binary_to_int(min_term))
    
    terms_to_add = added_terms.copy()
    levels_of_minterms = [min_terms]
    for i in range(0,num_vars+1):
        current_level = []
        if len(levels_of_minterms[i]) == 0:
            break
        for idx,min_term in enumerate(levels_of_minterms[i]):
            for idx_2,min_term_2 in enumerate(levels_of_minterms[i]):
                if idx != idx_2:
                    if binary_dist(min_term[0],min_term_2[0]) == 1:
                        combined_terms = combine_lists(min_term[1],min_term_2[1])
                        if combined_terms not in added_terms:
                            current_level.append([simplify_two_vars(min_term[0],min_term_2[0]),combined_terms])
                            added_terms.append(combined_terms)
        levels_of_minterms.append(current_level)
    levels_of_minterms = list(reversed(levels_of_minterms[:-1]))
    best_terms = []
    terms_added = []
    for term in terms_to_add:
        if term not in terms_added:
            best_term = find_best_term(levels_of_minterms,term)
            best_terms.append(best_term)
            for term in best_term[1]:
                if term not in terms_added:
                    terms_added.append(term)
    new_variables = []
    for var in variables:
        new_variables.append(Input(var.name))
    
    answer = None
    for term in best_terms:
        minterm = minterm_to_vars(term[0],new_variables)
        if answer is None:
            answer = minterm
        else:
            answer = answer + minterm
    if answer is None:
        return Zero()
    return answer