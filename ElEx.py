from bool_log import *
import re
import copy

to_remove = ['\*','\(','\)','\+','~','>>']
input_axioms = ['x*y*z+kareem','y*z','x>>(x+y)']
to_prove = '~(x*z)>>kareem'


def get_vars(string):
    variables = set([])
    for r in to_remove:
        string = re.sub(r,' ',string)
    string = string.split(" ")
    for var in string:
        if len(var) > 0:
            variables.add(var)
    return variables
        

class Statement:
    def __init__(self,expression,number,prefix='',desc=''):
        self.expression = expression
        self.number = str(number)+"."
        self.prefix = prefix
        self.desc = desc
        
    def __str__(self):
        return self.prefix + self.number + " " + str(self.expression)+"         "+self.desc
    
def check_conflict(statements):
    simples = []
    simple_nots = []
    simple_nots_idx = []
    simples_idx = []
    for idx,s in enumerate(statements):
        stat = s.expression
        if type(stat) is Input:
            simples.append(stat.name)
            simples_idx.append(idx)
        elif type(stat) is NOT and type(stat.inbound_vars[0]) is Input:
            simple_nots.append(stat.inbound_vars[0].name)
            simple_nots_idx.append(idx)
    for idx,s in enumerate(simple_nots):
        if s in simples:
            s1 = statements[simples_idx[simples.index(s)]]
            s1_str = s1.prefix + s1.number + " " + str(s1.expression)
            s2 = statements[simple_nots_idx[idx]]
            s2_str = s2.prefix + s2.number + " " + str(s2.expression)
            return True, "Conflict in branch between statements {} and {}".format(s1_str,s2_str)
    return False,None

class CustomStatement:
    def __init__(self,desc):
        self.desc = desc
    
    def __str__(self):
        return self.desc

def one_expansion_cycle(statements_arr,simplified,counter=0,prefix=''):
    to_expand = statements_arr
    #counter = len(to_expand) + 1
    to_branch = []
    for idx,s in enumerate(statements_arr):
        statement = s.expression
        if not statement.expanded:
            if type(statement) is AND:
                statement.expanded = True
                to_expand.append(Statement(statement.inbound_vars[0],counter,prefix,"By expanding "+s.prefix+s.number))
                to_expand.append(Statement(statement.inbound_vars[1],counter+1,prefix,"By expanding "+s.prefix+s.number))
                counter += 2
            elif  type(statement) is OR:
                to_branch.append(idx)
            elif  type(statement) is NOT:
                if type(statement.inbound_vars[0]) is AND:
                    to_branch.append(idx)
                elif type(statement.inbound_vars[0]) is OR:
                    statement.expanded = True
                    to_expand.append(Statement(~statement.inbound_vars[0].inbound_vars[0],counter,prefix,"By expanding "+s.prefix+s.number))
                    to_expand.append(Statement(~statement.inbound_vars[0].inbound_vars[1],counter+1,prefix,"By expanding "+s.prefix+s.number))
                    counter += 2
                elif type(statement.inbound_vars[0]) is NOT:
                    statement.expanded = True
                    to_expand.append(Statement(statement.inbound_vars[0].inbound_vars[0],counter,prefix,"By expanding "+s.prefix+s.number))
                    counter += 1
                elif  type(statement.inbound_vars[0]) is IMPLICATION:
                    statement.expanded = True
                    to_expand.append(Statement(statement.inbound_vars[0].inbound_vars[0],counter,prefix,"By expanding "+s.prefix+s.number))
                    to_expand.append(Statement(~statement.inbound_vars[0].inbound_vars[1],counter+1,prefix,"By expanding "+s.prefix+s.number))
                    counter += 2
                elif type(statement.inbound_vars[0]) is Input:
                    simplified.add(statement)
            elif type(statement) is IMPLICATION:
                to_branch.append(idx)
            elif type(statement) is Input:
                #statement.expanded = True
                simplified.add(statement)
                
    # Check for a conflict here
    is_conflict, conflict_desc = check_conflict(to_expand)
    if is_conflict:
        to_expand.append(Statement(CustomStatement(conflict_desc),counter,prefix))
        return to_expand, None
    # No conflict found, try to branch if branch needed
    if len(to_branch) > 0:
        to_expand[to_branch[0]].expression.expanded = True
        branch_left = copy.deepcopy(to_expand)
        branch_right = copy.deepcopy(to_expand)
        prefix_l = prefix+str(counter)+'.'
        prefix_r = prefix+str(counter+1)+'.'
        counter += 2
        
        branch_s = to_expand[to_branch[0]]
        branch_statement = branch_s.expression
        if type(branch_statement) is OR:
            branch_left.append(Statement(branch_statement.inbound_vars[0],0,prefix_l, "Left branch of "+branch_s.prefix+branch_s.number))
            branch_right.append(Statement(branch_statement.inbound_vars[1],0,prefix_r, "Right branch of "+branch_s.prefix+branch_s.number))
        elif type(branch_statement) is NOT:
            if type(branch_statement.inbound_vars[0]) is AND:
                branch_left.append(Statement(~branch_statement.inbound_vars[0].inbound_vars[0],0,prefix_l, "Left branch of "+branch_s.prefix+branch_s.number))
                branch_right.append(Statement(~branch_statement.inbound_vars[0].inbound_vars[1],0,prefix_r, "Right branch of "+branch_s.prefix+branch_s.number))
        elif  type(branch_statement) is IMPLICATION:
            branch_left.append(Statement(branch_statement.inbound_vars[0],0,prefix_l, "Left branch of "+branch_s.prefix+branch_s.number))
            branch_right.append(Statement(~branch_statement.inbound_vars[1],0,prefix_r, "Right branch of "+branch_s.prefix+branch_s.number))

        to_expand_l,ce_l = one_expansion_cycle(branch_left,simplified.copy(),prefix=prefix_l,counter=1)
        to_expand_r,ce_r = one_expansion_cycle(branch_right,simplified.copy(),prefix=prefix_r,counter=1)
        to_expand_len = len(to_expand)
        to_expand.append([to_expand_l[to_expand_len:],to_expand_r[to_expand_len:]])
        if ce_l is not None:
            return to_expand,ce_l
        if ce_r is not None:
            return to_expand,ce_r
    else:
        simples = []
        for idx,s in enumerate(to_expand):
            stat = s.expression
            if type(stat) is Input:
                simples.append(stat.name+'=True')
            elif type(stat) is NOT and type(stat.inbound_vars[0]) is Input:
                simples.append(stat.inbound_vars[0].name+'=False')
        to_expand.append(Statement(CustomStatement('Branch open, Counter Example found'),counter,prefix))
        return to_expand, list(set(simples))
    
    return to_expand, None


def statements_to_str(to_print):
    strs = []
    for s in to_print:
        if type(s) is Statement or type(s) is CustomStatement:
            strs.append(str(s))
        else:
            strs.append(statements_to_str(s))
    return strs

def solver(input_axioms,to_prove):
    valid = True


    variables = set([])
    for s in input_axioms:
        variables = variables.union(get_vars(s))
    variables = list(variables)

    to_exec = []
    for var in variables:
        to_exec.append(var+'=Input("'+var+'")')

    axioms_exec = 'axioms = ['+",".join(input_axioms)+']'
    to_exec.append(axioms_exec)
    to_exec.append('statements = axioms.copy()')

    to_prove_vars = get_vars(to_prove)
    for v in to_prove_vars:
        if v not in variables:
            valid = False
            print("Unknown Variable {} in statement to prove".format(v))

    to_exec.append('statements.append(~('+to_prove+'))')

    for e in to_exec:
        exec(e,globals())
        
    statements_arr = []
    for idx,s in enumerate(statements):
        statements_arr.append(Statement(s,idx+1)) 
        
    simplified = set([])
    to_expand,ce = one_expansion_cycle(statements_arr,simplified,counter=len(statements_arr)+1)
    to_return_expand = statements_to_str(to_expand)
        
    to_return_ce = ""
    if ce is not None:
        for s in ce:
            to_return_ce += str(s) + ' '
    return to_return_expand,to_return_ce
