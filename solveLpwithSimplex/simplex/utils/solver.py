import pulp


def lp_solver(objective, constraints):
    """
    :param objective: [[0, 1], ['max']]
    :param constraints: [[0, 1, '<=', 25], [0, 1, '<=', 25]]
    :return:
    """
    variable_count = len(objective[0])

    lp_sense = -1 if objective[1][0] == "max" else 1
    lp = pulp.LpProblem('lp', sense=lp_sense)

    variables = list()

    for i in range(variable_count):
        variables.append(pulp.LpVariable(name="x" + str(i), lowBound=0))

    lp += objective_function(objective[0], variables)

    for i in range(len(constraints)):
        lp += constraint_function(constraints[i], variables)

    lp.solve()

    result = dict()

    result['lp'] = lp
    result['status'] = pulp.LpStatus[lp.status]
    result['solution_time'] = round(lp.solutionTime, 2)

    variables_value = dict()
    variables_value_list = list()

    for variable in lp.variables():
        variables_value[variable.name] = variable.varValue
        variables_value_list.append(variable.varValue)

    result['variables_value'] = variables_value
    result['variables_value_list'] = variables_value_list
    result['objective_value'] = pulp.value(lp.objective)

    return result


def objective_function(objective, variables):
    objective_func = ""

    for obj, var in zip(objective, variables):
        objective_func += obj * var

    return objective_func


def constraint_function(constraint, variables):
    constraint_func = ""
    constrain_sense = None

    if constraint[-2] == '<=':
        constrain_sense = pulp.LpConstraintLE
    elif constraint[-2] == '=':
        constrain_sense = pulp.LpConstraintEQ
    else:
        constrain_sense = pulp.LpConstraintGE

    for cons, var in zip(constraint[0], variables):
        constraint_func += cons * var

    return pulp.LpConstraint(e=constraint_func, sense=constrain_sense, rhs=constraint[-1])