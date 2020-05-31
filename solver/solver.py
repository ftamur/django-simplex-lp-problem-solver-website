import numpy as np

# ignore dividing with zero error
np.seterr(divide='ignore', invalid='ignore')


class LpProblem():

    def __init__(self, sense='max'):
        """
        Initializes a lp problem. 

        Parameters: sense: str -> could be ['max', 'min']

        Returns: None
        """
        self.Z = 0
        self.sense = sense
        self.table = []
        self.tableau = None
        self.two_phase = False
        self.status = "Unsolved"


    def objective(self, obj):
        """
        Set objective parameters.

        Parameters: obj: list[float] 
                         len: n

        Returns: None
        """

        self.objective = obj
        self.n = len(obj)
        self.table.append(obj)


    def constraints(self, constraints):
        """
        Set constraint parameters.

        Parameters: constraints: list[list[float]] 
                                 len: m
                                 len: n

        Returns: None
        """

        self.constraints = constraints
        self.m = len(constraints)
        

    def constraint_senses(self, senses):
        """
        Set constraint senses.

        Parameters: senses: list[str]
                            len: m

        Returns: None
        """
        
        self.const_senses = senses


    def rhs(self, rhs):
        """
        Set right hand side values for constraints.

        Parameters: rhs: list[float]
                         len: m

        Return: None
        """

        self.RHS = rhs
        
        for i in range(len(rhs)):
            if rhs[i] < 0:
                print(i)
                self.constraints[i] = [r * -1 for r in self.constraints[i]]
                self.RHS[i] = rhs[i] * -1
                
                if self.const_senses[i] == '<=':
                    self.const_senses[i] = '>='
                elif self.const_senses[i] == '>=':
                    self.const_senses[i] = '<='
                    
        self.RHS.insert(0, self.Z)
                

    def _tableau_format(self):
        """
        Adds slack variables. 

        Parameters: None

        Return: None
        """
        
        self.table.extend(self.constraints)
        
        # add slack variables
        for i in range(self.m+1):
            self.table[i].extend([0]*self.m)
            
        for i, eq in enumerate(self.table[1:]):
            eq[i+self.n] = 1

        # initialize tableau array.
        self.tableau = np.array(self.table, dtype=float)
        
        self.RHS = np.array(self.RHS)
        
        self.tableau = np.hstack((self.table, self.RHS[:, np.newaxis]))
        
        self.nonbasics = list(range(self.n)) 
        self.basics = list(range(self.n, self.n + self.m))
        
        if self.sense == 'min':
            self.find_dual()
   
        if not all(sense == '<=' for sense in self.const_senses):
            self.two_phase = True
            
         
    def _add_artificials(self):
        """
        Adds artificals if initial basic solution is not feasible.

        Parameters: None

        Returns: None
    
        """
        
        self.artifical_count = 0
        self.artifical_indexes = []
        self.sense_equals = 0
        
        for i, sense in enumerate(self.const_senses):
             
            if sense == '==':
                # add artifical variable
                col = np.zeros((self.m+1, 1))
                col[0] = 1
                col[i+1] = 1
                  
                self.tableau = np.hstack((np.hstack((self.tableau[:, :self.n+i], col)), self.tableau[:, self.n+i+1:]))
                    
                self.artifical_count += 1
                self.sense_equals += 1
                
            elif sense == '>=':
                # add slack variable
                col = np.zeros((self.m+1, 1))
                col[i+1] = -1
                
                self.tableau = np.hstack((np.hstack((self.tableau[:, :self.n], col)), self.tableau[:, self.n:]))
                
                self.n += 1
                
                # add artifical variable
                col = np.zeros((self.m+1, 1))
                col[0] = 1
                col[i+1] = 1
                  
                self.tableau = np.hstack((np.hstack((self.tableau[:, :self.n+i], col)), self.tableau[:, self.n+i+1:]))
                  
                self.artifical_count += 1
                
        
        self.nonbasics = list(range(self.n)) 
        self.basics = list(range(self.n, self.n + self.m))        
        self.artifical_indexes = list(set(list(np.where(self.tableau[0] == 1)[0])).intersection(self.basics))
        
        # set row to 0
        self.tableau[0, :self.n] = np.zeros((self.n))
        
        # eliminate artificial ones in the row 0
        for i in self.artifical_indexes:
            self.tableau[0] -= self.tableau[self.basics.index(i)+1]
            
        # convert to -Z to Z 
        self.tableau[0] *= -1
            
            
    def remove_artificials(self):
        """
        Removes artificals variables from tableau.
        
        Parameters: None
        
        Returns: None
        """
        
        self.tableau = np.delete(self.tableau, self.artifical_indexes, axis=1)
                
        for i in self.artifical_indexes:
            if i in self.basics:
                self.basics[self.basics.index(i)] = self.nonbasics[i]
                del self.nonbasics[i]
              
            
        for basic in self.basics:
            if any(v < basic for v in self.artifical_indexes):
                self.basics[self.basics.index(basic)] -= self.artifical_count
              
           
        
    def remove_inconsistency(self, obj):
        """
        Sets obj values to row 0 in tableau. 
        Removes inconsistency between row 0 and basic variables.
        
        Parameters: obj: np.ndarray((n, m), dtype='float')
        
        Returns: None
        """
        
        if self.sense_equals > 0:
            self.tableau[0] = obj[:-self.sense_equals]
        else:
            self.tableau[0] = obj
            
            
        for basic in self.basics:
            if np.inf == (self.tableau[0, basic] / self.tableau[self.basics.index(basic)+1, basic]):
                return False

            self.tableau[0] -= (self.tableau[0, basic] / self.tableau[self.basics.index(basic)+1, basic]) * self.tableau[self.basics.index(basic)+1, :]
           
        
        return True
    
    
    def find_dual(self):
            
        for i in range(len(self.const_senses)):
            if self.const_senses[i] == '>=':
                self.const_senses[i] = '<='
            elif self.const_senses[i] == '<=':
                self.tableau[i+1] = -self.tableau[i+1]
                self.const_senses[i] = "<="
                                            
        tableu_copy = np.zeros((self.n + 1, self.m + self.n + 1))
    
        tableu_copy[0, :self.m] = self.tableau[1:, -1]    
        tableu_copy[1:, :self.m] = np.transpose(self.tableau[1:, :self.n])
        tableu_copy[1:, -1] = np.transpose(self.tableau[0, :self.n])
        tableu_copy[1:, self.m:self.m+self.n] = np.eye(self.n)
        
        self.tableau = tableu_copy
        self.m, self.n = self.n, self.m
        
        self.nonbasics = list(range(self.n)) 
        self.basics = list(range(self.n, self.n + self.m))
          
            
    def _B_inv(self):
        return np.linalg.inv(self.tableau[1:, self.basics])
    
    
    def _A(self):
        return self.tableau[1:, self.nonbasics]
    
    
    def _c_b(self):
        return self.tableau[0, self.basics]
    
    
    def _c_n(self):
        return self.tableau[0, self.nonbasics]

         
    def _simplex(self):
        """
        Applys revised simplex method until Optimal point found or solution infeasible.

        Parameters: None

        Returns: None
        """
 
        # find B inverse
        B_inv = self._B_inv()
        iteration = 0
        
        while np.any(self.tableau[0, self.nonbasics] > 0):
            
        
            # update RHS
            x_b = np.dot(B_inv, self.tableau[1:, -1])
            
            if iteration > 0 and self.tableau[0, -1] == 0:
                return 
                
            # update Z
            self.tableau[0, -1] = np.dot(self._c_b(), x_b)
            
            # w = c_b * B_inv
            w = np.dot(self._c_b(), B_inv)
                        
            # z_n - c_n = w * A - c_n
            z_n_c_n = self._c_n() - np.dot(w, self._A())
            
            if all(z_n_c_n <= 0):
                self.status = "Optimal"
                break
                        
            # find entering variable
            pivot_col = np.argmax(z_n_c_n)
            
            # update A
            A = np.dot(B_inv, self._A())
                       
            # rhs / pivot_col
            theta = x_b / A[:, pivot_col]
            
            if all(theta <= 0):
                self.status = 'Unbounded'
                return
            
            theta[theta < 0] = np.inf 
                
            # find leaving variable
            pivot_row = np.argmin(theta)
                        
            # find n to create E 
            n = A[:, pivot_col] * -(1 / A[pivot_row][pivot_col])
            
            # set pivot element positive value
            n[pivot_row] = (1 / A[pivot_row][pivot_col])
                        
            # create identity matrix for E
            E = np.eye(self.m)
            
            E[:, pivot_row] = n
                        
            B_inv = np.dot(E, B_inv)
                        
            enters = self.nonbasics[pivot_col]
            leaves = self.basics[pivot_row]
            
            self.basics[pivot_row] = enters
                        
            self.nonbasics[pivot_col] = leaves
            
            iteration += 1

        # update RHS
        x_b = np.dot(B_inv, self.tableau[1:, -1])

        # update Z
        self.tableau[0, -1] = np.dot(self._c_b(), x_b)
        
        # update RHS
        self.tableau[1:, -1] = x_b
    
        self.Z = self.tableau[0, -1]
        
        sol = {}
        
        for i in range(self.m):
            sol[self.basics[i]] = list(x_b)[i]
        
        self.solution = list(range(self.n + self.m))
        
        for i in range(len(self.solution)):
            if i in sol.keys():
                self.solution[i] = sol[i]
            else:
                self.solution[i] = 0
            
        self.status = "Optimal"

    def solve(self):
        """
        Solves lp problem. Applies two phase method if needed.

        Parameters: None

        Returns: None
        """

        # if initial bfs solve in 1 phase
        if not self.two_phase:
            self._simplex()
            return

        # save objective for 2nd phase
        obj = self.tableau[0]
        
        print(obj)
        
        # if no initial bfs then add artificials.
        self._add_artificials()
        
        # 1st Phase
        self._simplex()
    
        # remove artificials and set initial objective
        self.remove_artificials()
        
        # remove inconsistency
        # if we can not remove inconsistency we return infeasible
        if not self.remove_inconsistency(obj):
            self.status = "infeasible"
            return
        
        # 2nd Phase
        self._simplex()        
