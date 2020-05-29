import numpy as np

"""
Input types and shapes

n: variable count
m: constraint count

Sense: string

Objective:

type: float
np.array - shape: (1, n)

Constrainst's Sense:

type: string
np.array - shape: (1, m)

Constrainst:

type: float
np.array - shape: (m, n)


Right Hand Sides:


type: float
np.array - shape: (1, m)


"""

"""
Local variables' types and shapes

n: variable count
m: constraint count




"""


class Lp_Problem:

    def __init__(self, name: str, sense: str):
        self.name = name
        self.sense = sense
        self.z = 0
        self.artificals = []
        self.basics = []
        self.non_basics = []
        self.table = None
        self.two_phase = False
    

    def objective(self, obj_coeff: np.ndarray) -> None:
        """
        Objective:
        
        type: float
        np.array - shape: (1, n)
        
        Example:
        
        np.array([[3, 4, 5]])
        
        """
        
        # if sense is min convert it to max with changing c_n = -c_n
        if self.sense == 'min':
            self.c_n = -obj_coeff.astype('float64')
        else:
            self.c_n = obj_coeff.astype('float64')
            
        # n is variable count
        self.n = obj_coeff.shape[1]

        
    def constraint_sense(self, const_sense: np.ndarray) -> None:
        """      
        Constrainst's Sense:

        type: string
        np.array - shape: (m, 1)
        
        Example:
        
        np.array([['<='], ['<='], ['<=']])
        
        """
        
        if '>=' in const_sense or '==' in const_sense:
            # if initial solution not feasible then we will apply two-phase
            self.two_phase = True
            
            # set c_n to 0 because we will fix it in the initialization
            self.c_n = np.dot(self.c_n, 0) 
                
        self.const_sense = const_sense
    
    def constraint(self, const_coeff: np.ndarray) -> None:
        """
        Constrainst:

        type: float
        np.array - shape: (m, n)
        
        Example:
        
        np.array([[8, 9, 2],
                  [32, 42, 3],
                  [3, 2, 4]])
        
        """
        # m is constraint count
        self.m = const_coeff.shape[0]
        self.A = const_coeff.astype('float64')
        
    def rhs(self, rhs: np.ndarray) -> None:
        """
        Right Hand Sides:

        type: float
        np.array - shape: (m, 1)
        
        Example:
        
        np.array([[3], [6], [4]])
        
        """
        self.x_b = rhs
        
        
    def initialization(self):
        self.B_inv = np.zeros(shape=(self.m, 0))
        self.c_b = np.zeros(shape=(1, 0))
        self.artificals_count = 0
        
        for constraint in range(self.m):

            col = np.zeros((self.m, 1))
            
            if self.const_sense[0][constraint] == '==':
                
                print("==")
                self.basics.append(self.c_n.shape[1] + self.artificals_count + self.c_b.shape[1])
                self.artificals.append(self.c_n.shape[1] + self.artificals_count + self.c_b.shape[1])
                self.c_b = np.hstack((self.c_b, [[0]]))
                
                # update basics variables to first step
                self.c_n[:, 0:self.c_n.shape[1]] += self.A[self.artificals_count, 0:self.c_n.shape[1]]
                        
                col[constraint] = 1
                self.B_inv= np.hstack((self.B_inv, col))
                
                self.two_phase = True
                self.artificals_count += 1
            elif self.const_sense[0][constraint] == '>=':
                
                print(">=")
                
                # update basics variables to first step
                self.c_n[:, 0:self.c_n.shape[1]] += self.A[self.artificals_count, 0:self.c_n.shape[1]]

                self.basics.append(self.c_n.shape[1] + self.artificals_count + self.c_b.shape[1])
                self.artificals.append(self.c_n.shape[1] + self.artificals_count + self.c_b.shape[1])
                self.c_b = np.hstack((self.c_b, [[0]]))
                
                self.c_n = np.hstack((self.c_n, [[0]]))
                
                for i in range(self.c_b.shape[1]):
                    self.basics[i] += 1
                
                col[constraint] = -1
                self.A = np.hstack((self.A, col))

                col[constraint] = 1
                self.B_inv = np.hstack((self.B_inv, col))
                    
                self.two_phase = True
                self.artificals_count += 1
            else:
                
                print("<=")
                for i in range(self.c_b.shape[1]):
                    self.basics[i] += 1
                    
                for i in range(len(self.artificals)):
                    self.artificals[i] += 1
                    
                self.basics.append(self.c_n.shape[1])
                self.c_b = np.hstack(([[0]], self.c_b))
                
                col[constraint] = 1
                self.B_inv = np.hstack((col, self.B_inv))
                
        
        self.non_basics = list(range(0, self.c_n.shape[1]))
        self.table = np.zeros(shape=(self.m + 1, self.c_b.shape[1] + self.c_n.shape[1] + 1))
        
        
    def build_table(self):
        non_basics = self.A.shape[1]
        basics = self.c_b.shape[1]
     
        self.table[0, 0:non_basics] = self.c_n 
        self.table[0, non_basics:non_basics+basics] = self.c_b
        self.table[1:self.m+1, 0:self.A.shape[1]] = self.A
        self.table[1:self.m+1, self.A.shape[1]:self.A.shape[1] + self.B_inv.shape[0]] = self.B_inv
        self.table[1:self.m+1, non_basics + basics:non_basics + basics + 1] = self.x_b
        
        print(self.table)
             
            
    def simplex(self):
        
        if self.two_phase:
            self.c_n = -self.c_n
            
                          
    def remove_artificals(self):
        b_indexes = list(range(self.B_inv.shape[1]-1, self.B_inv.shape[1]-self.artificals_count-1 ,-1))
        c_b_indexes = list(range(self.c_b.shape[1]-1, self.c_b.shape[1]-self.artificals_count-1 ,-1))
        
        np.delete(self.B_inv, b_indexes, axis=1)
        np.delete(self.c_b, c_b_indexes, axis=1)
        
        self.build_table()    
        
    def dual_lp(self):
        """
        Converts a Lp problem to its dual problem. 
        """
        
        objective = np.copy(self.c_n)
        constraints = np.copy(self.A)
        rhs = np.copy(self.x_b)
    
        self.c_n = rhs
        self.A = np.transpose(constraints)
        self.x_b = objective
        
        
    def print_lp(self):
        """
        Prints lp problem with variables and coefficents.
        """
        
        obj_str = ""

        for i, coeff in enumerate(self.c_n[0]):
            obj_str += str(coeff) + " * x_" + str(i) + " + "

        obj_str = obj_str.strip("+ ")
        
        print("Objective: ", obj_str)
        print("Sense: ", self.sense)
        
        print("Constraints: ")
        
        rhs_count = 0
        
        for constraint in self.A:
            const_str = ""
            
            for i, coeff in enumerate(constraint):
                const_str += str(coeff) + " * x_" + str(i) + " + "

            const_str = const_str.strip("+ ")
            const_str += " " + str(self.const_sense[0][rhs_count]) + " " + str(self.x_b[rhs_count][0])
            
            rhs_count += 1
            print(const_str)
                    
    def solve(self):    
        self._set_B_inv_and_c_n()
        
        # if the origin is feasible not need to 2-Phase method.
        if not self.two_phase:
            self.simplex()
            return
        
        print("1 - Phase...")
        self.simplex()
                
        self.two_phase = False
            
        print("2 - Phase...")
        self.simplex()
        
        print("Lp - Solved.")
        

obj = np.array([[4, 1]])


constraints = np.array([[3, 1],
                        [4, 3],
                        [1, 2]])

contraints_sense = np.array([['==', '>=', '<=']])

rhs = np.array([[3], [6], [4]])


lp = Lp_Problem('firat', 'max')
lp.objective(obj)
lp.constraint(constraints)
lp.constraint_sense(contraints_sense)
lp.rhs(rhs)
lp.print_lp()


lp.initialization()
