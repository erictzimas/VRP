from VRP_Model import *
from SolutionDrawer import *

class SwapMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9

class RelocationMove(object):
    def __init__(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = None

    def Initialize(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = 10 ** 9

class Solution:
    def __init__(self):
        self.cost = 0.0
        self.profit = 0.0
        self.routes = []


class CustomerInsertion(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.cost = 10 ** 9
        self.profit = 0
        

class Solver:
    def __init__(self, m):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.profit = m.profit
        self.capacity = m.capacity
        self.sol = None
        self.bestSolution = None
        self.overallBestSol = None
        self.searchTrajectory = []
        self.rcl_size = 3

    def solve(self):
        for i in range(20):
            self.SetRoutedFlagToFalseForAllCustomers()
            self.ApplyNearestNeighborMethod(i)
            cc = self.sol.cost
            print(i, 'Constr:', self.sol.cost)
            #self.LocalSearch(0)
            #self.LocalSearch(1)
            self.VND()
            
            if self.overallBestSol == None or self.overallBestSol.profit < self.sol.profit:
                self.overallBestSol = self.cloneSolution(self.sol)
            print(i, 'Const: ', cc, ' LS:', self.sol.profit, 'BestOverall: ', self.overallBestSol.profit)
            print(i, 'Prof : ', self.sol.profit)
            SolDrawer.draw(i, self.sol, self.allNodes)
            self.TestSolution()
        self.sol = self.overallBestSol
        self.ReportSolution(self.sol)
        SolDrawer.draw(10000, self.sol, self.allNodes)
        return self.sol
#0 46 63 23 164 13 101 0
#Total profit : 414.0
#Total cost : 691.5649424224906
    def SetRoutedFlagToFalseForAllCustomers(self):
        for i in range(0, len(self.customers)):
            self.customers[i].isRouted = False

    def ApplyNearestNeighborMethod(self, itr = 0):
        modelIsFeasible = True
        self.sol = Solution()
        insertions = 0
        count = 0
        while (insertions < len(self.customers)):
            bestInsertion = CustomerInsertion()
            lastOpenRoute: Route = self.GetLastOpenRoute()
        
            if lastOpenRoute is not None:
                self.IdentifyBest_NN_ofLastVisited(bestInsertion, lastOpenRoute, itr)

            if (bestInsertion.customer is not None):
                self.ApplyCustomerInsertion(bestInsertion)
                #print(bestInsertion.route.load)
                insertions += 1

            else:
                #If there is an empty available route
                if lastOpenRoute is not None and len(lastOpenRoute.sequenceOfNodes) == 2:
                    modelIsFeasible = False
                    break
                else:
                    count+= 1
                    
                        
                    rt = Route(self.depot, self.capacity, self.profit)
                       
                    self.sol.routes.append(rt)
                    
                    if count > 5:
                        break
                    
                    
                    
                    
                    
        
        if (modelIsFeasible == False):
            print('FeasibilityIssue')
            #reportSolution

    

    def cloneRoute(self, rt:Route):
        cloned = Route(self.depot, self.capacity, self.profit)
        cloned.cost = rt.cost
        cloned.load = rt.load
        cloned.profit = rt.profit
        cloned.sequenceOfNodes = rt.sequenceOfNodes.copy()
        return cloned

    def cloneSolution(self, sol: Solution):
        cloned = Solution()
        for i in range (0, len(sol.routes)):
            rt = sol.routes[i]
            clonedRoute = self.cloneRoute(rt)
            cloned.routes.append(clonedRoute)
        cloned.cost = self.sol.cost
        cloned.profit = self.sol.profit
        return cloned

    
    def ReportSolution(self, sol):
        #print("No of ROUTES :: " + str(len(sol.routes)))
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            #print(rt)
            for j in range (0, len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=' ')
            
            print('\n')
            print('Profit per Route : ' + str(rt.profit))
            print('Load per Route : ' + str(rt.load))
            print('Cost per route : ' + str(rt.cost))
        print ('Total profit : ' + str(self.sol.profit))
        print('Total cost : ' + str(self.sol.cost))
        

    def GetLastOpenRoute(self):
        if len(self.sol.routes) == 0:
            return None
        else:
            return self.sol.routes[-1]

    def IdentifyBest_NN_ofLastVisited(self, bestInsertion, rt, itr = 0):
        random.seed(itr)
        rcl = []
        for i in range(0, len(self.customers)):
            candidateCust:Node = self.customers[i]
            if candidateCust.isRouted is False:
                beforeInserted = rt.sequenceOfNodes[-2]
                loadAdded = self.distanceMatrix[beforeInserted.ID][candidateCust.ID] + self.distanceMatrix[candidateCust.ID][self.depot.ID]
                loadRemoved = self.distanceMatrix[beforeInserted.ID][self.depot.ID]
                if rt.load + candidateCust.service_time + loadAdded - loadRemoved<= rt.capacity:
                    lastNodePresentInTheRoute = rt.sequenceOfNodes[-2]
                    trialCost = self.distanceMatrix[lastNodePresentInTheRoute.ID][candidateCust.ID] + candidateCust.service_time
                    # Update rcl list
                    if len(rcl) < self.rcl_size:
                        new_tup = (trialCost, candidateCust, rt, candidateCust.profit)
                        rcl.append(new_tup)
                        rcl.sort(key=lambda x: x[0])
                    elif trialCost < rcl[-1][0]:
                        rcl.pop(len(rcl) - 1)
                        new_tup = (trialCost, candidateCust, rt, candidateCust.profit)
                        rcl.append(new_tup)
                        rcl.sort(key=lambda x: x[0])
        
        if len(rcl) > 0:
            
            tup_index = random.randint(0, len(rcl) - 1)
            tpl = rcl[tup_index]
            
            #print(tpl)
            insCustomer = tpl[1]
            beforeInserted = rt.sequenceOfNodes[-2]
            loadAdded = self.distanceMatrix[beforeInserted.ID][insCustomer.ID] + self.distanceMatrix[insCustomer.ID][self.depot.ID]
            loadRemoved = self.distanceMatrix[beforeInserted.ID][self.depot.ID]
            #rt.load += loadAdded - loadRemoved
            if rt.load +loadAdded - loadRemoved + candidateCust.service_time  < rt.capacity:
                #print(tpl)
                bestInsertion.cost = tpl[0]
                bestInsertion.customer = tpl[1]
                bestInsertion.route = tpl[2]
                
                #print('Best insertion load : ' + str(bestInsertion.route.load ))



    def ApplyCustomerInsertion(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        #before the second depot occurrence
        insIndex = len(rt.sequenceOfNodes) - 1
        rt.sequenceOfNodes.insert(insIndex, insCustomer)

        beforeInserted = rt.sequenceOfNodes[-3]
        #print(insCustomer.ID)
        #print(beforeInserted.ID)
        
        #self.sol.cost += costAdded 

        #print('RT COST : ' + str(self.sol.cost))

        loadAdded = self.distanceMatrix[beforeInserted.ID][insCustomer.ID] + self.distanceMatrix[insCustomer.ID][self.depot.ID]
        loadRemoved = self.distanceMatrix[beforeInserted.ID][self.depot.ID]


        rt.load += loadAdded - loadRemoved + insCustomer.service_time
        rt.cost += loadAdded - loadRemoved + insCustomer.service_time
        self.sol.cost += loadAdded - loadRemoved + insCustomer.service_time

        rt.profit += insCustomer.profit
        self.sol.profit += insCustomer.profit

        #print(rt.profit)
        

        insCustomer.isRouted = True
    


    ### RELOCATE -- SWAP -- INSERTION -- PROFITABLE SWAP

    ## Relocate
    def InitializeOperators(self, rm, sm):
        rm.Initialize()
        sm.Initialize()

    def TestSolution(self):
        totalSolCost = 0
        for r in range (0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            rtCost = 0
            rtLoad = 0
            rtProfit = 0 
            for n in range (0 , len(rt.sequenceOfNodes) - 1):
                A = rt.sequenceOfNodes[n]
                B = rt.sequenceOfNodes[n + 1]
                rtCost += A.service_time + self.distanceMatrix[A.ID][B.ID] 
                rtLoad += A.service_time + self.distanceMatrix[A.ID][B.ID]
                rtProfit += A.profit
            
            #print('Route load : ' + str(rt.load) + '   Route cost : ' + str(rt.cost) + ' Route profit : ' + str(rt.profit))
            #print('Route Correct Profit : ' + str(rtProfit) + '   Route Accumulated Profit : ' + str(rt.profit))
            #print('Route correct cost : ' + str(rtCost) + '   Route accumulated cost : ' + str(rt.cost))
            if abs(rtCost - rt.cost) > 0.0001:
                print ('Route Cost problem')
            if abs(rtLoad - rt.load) > 0.0001:
                print ('Route Load problem')
            if abs(rtProfit - rt.profit) > 0.0001:
                print ('Route Profit problem')

            totalSolCost += rt.cost

        if abs(totalSolCost - self.sol.cost) > 0.0001:
            print('Solution Cost problem')

    def LocalSearch(self, operator):
            self.bestSolution = self.cloneSolution(self.sol)
            terminationCondition = False
            localSearchIterator = 0

            rm = RelocationMove()
            sm = SwapMove()
            

            while terminationCondition is False:

                self.InitializeOperators(rm, sm)
                # SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

                # Relocations
                if operator == 0:
                    self.FindBestRelocationMove(rm)
                    if rm.originRoutePosition is not None:
                        #print(rm.moveCost)
                        if rm.moveCost < 0:
                            
                            self.ApplyRelocationMove(rm)
                        else:
                            terminationCondition = True
                # Swaps
                elif operator == 1:
                    self.FindBestSwapMove(sm)
                    if sm.positionOfFirstRoute is not None:
                        if sm.moveCost < 0:
                            self.ApplySwapMove(sm)
                        else:
                            terminationCondition = True

                self.TestSolution()

                if (self.sol.cost < self.bestSolution.cost):
                    self.bestSolution = self.cloneSolution(self.sol)

                localSearchIterator = localSearchIterator + 1

            self.sol = self.bestSolution

    def FindBestRelocationMove(self, rm):
        for originRouteIndex in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[originRouteIndex]
            for targetRouteIndex in range (0, len(self.sol.routes)):
                rt2:Route = self.sol.routes[targetRouteIndex]
                for originNodeIndex in range (1, len(rt1.sequenceOfNodes) - 1):
                    for targetNodeIndex in range (0, len(rt2.sequenceOfNodes) - 1):

                        if originRouteIndex == targetRouteIndex and (targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
                            continue

                        A = rt1.sequenceOfNodes[originNodeIndex - 1]
                        B = rt1.sequenceOfNodes[originNodeIndex]
                        C = rt1.sequenceOfNodes[originNodeIndex + 1]

                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                        if rt1 != rt2:
                            if rt2.load + B.service_time > rt2.capacity:
                                continue
                        # AC + FB + BG
                        costAdded = self.distanceMatrix[A.ID][C.ID] + C.service_time + self.distanceMatrix[F.ID][B.ID] +  B.service_time + self.distanceMatrix[B.ID][G.ID] + G.service_time
                        costRemoved = self.distanceMatrix[A.ID][B.ID] +  B.service_time + self.distanceMatrix[B.ID][C.ID] +  C.service_time  + self.distanceMatrix[F.ID][G.ID]   +  G.service_time 
                        # - AC + AB + BC
                        originRtCostChange = self.distanceMatrix[A.ID][C.ID]  +  C.service_time  - self.distanceMatrix[A.ID][B.ID]  -  B.service_time  - self.distanceMatrix[B.ID][C.ID] - C.service_time
                        targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + B.service_time +  self.distanceMatrix[B.ID][G.ID] + G.service_time - self.distanceMatrix[F.ID][G.ID] - G.service_time
                        # - FB + BG + FG
                        
                        moveCost = costAdded - costRemoved
                        #print(moveCost)

                        if (moveCost < rm.moveCost):
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm)

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm:RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost
    
    def ApplyRelocationMove(self, rm: RelocationMove):

        oldCost = self.CalculateTotalCost(self.sol)

        originRt = self.sol.routes[rm.originRoutePosition]
        targetRt = self.sol.routes[rm.targetRoutePosition]

        B = originRt.sequenceOfNodes[rm.originNodePosition]

        if originRt == targetRt:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            if (rm.originNodePosition < rm.targetNodePosition):
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)
            else:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)

            originRt.cost += rm.moveCost
            originRt.load += rm.moveCost
            #originRt.profit += rm.moveCost
        else:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)

            originRt.cost += rm.costChangeOriginRt
            targetRt.cost += rm.costChangeTargetRt

            originRt.load += rm.costChangeOriginRt
            targetRt.load += rm.costChangeTargetRt

            originRt.profit -= B.profit
            targetRt.profit += B.profit

        #print(self.sol.profit)
        self.sol.cost += rm.moveCost
         
        ##print(self.sol.profit)
        #print('\n \n ')

        newCost = self.CalculateTotalCost(self.sol)
        #debuggingOnly
        if abs((newCost - oldCost) - rm.moveCost) > 0.0001:
            print('Cost Issue')

    def CalculateTotalCost(self, sol):
        c = 0
        for i in range (0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range (0, len(rt.sequenceOfNodes) - 1):
                a = rt.sequenceOfNodes[j]
                b = rt.sequenceOfNodes[j + 1]
                c += self.distanceMatrix[a.ID][b.ID]
        return c

    # SWAP

    def FindBestSwapMove(self, sm):
        for firstRouteIndex in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[firstRouteIndex]
            for secondRouteIndex in range (firstRouteIndex, len(self.sol.routes)):
                rt2:Route = self.sol.routes[secondRouteIndex]
                for firstNodeIndex in range (1, len(rt1.sequenceOfNodes) - 1):
                    startOfSecondNodeIndex = 1
                    if rt1 == rt2:
                        startOfSecondNodeIndex = firstNodeIndex + 1
                    for secondNodeIndex in range (startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):

                        a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                        b1 = rt1.sequenceOfNodes[firstNodeIndex]
                        c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]

                        a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                        b2 = rt2.sequenceOfNodes[secondNodeIndex]
                        c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]

                        moveCost = None
                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        if rt1 == rt2:
                            if firstNodeIndex == secondNodeIndex - 1:
                                costRemoved = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                costAdded = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]
                                moveCost = costAdded - costRemoved
                            else:

                                costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                                costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                                costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]
                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                        else:
                            if rt1.load - b1.service_time + b2.service_time > self.capacity:
                                continue
                            if rt2.load - b2.service_time + b1.service_time > self.capacity:
                                continue

                            costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                            costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                            costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                            costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]

                            costChangeFirstRoute = costAdded1 - costRemoved1
                            costChangeSecondRoute = costAdded2 - costRemoved2

                            moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                        if moveCost < sm.moveCost:
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

    def ApplySwapMove(self, sm):
        oldCost = self.CalculateTotalCost(self.sol)
        rt1 = self.sol.routes[sm.positionOfFirstRoute]
        rt2 = self.sol.routes[sm.positionOfSecondRoute]
        b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
        b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
        rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
        rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

        if (rt1 == rt2):
            rt1.cost += sm.moveCost
        else:
            rt1.cost += sm.costChangeFirstRt
            rt2.cost += sm.costChangeSecondRt
            rt1.load = rt1.load - b1.service_time + b2.service_time
            rt2.load = rt2.load + b1.service_time - b2.service_time

        self.sol.cost += sm.moveCost

        newCost = self.CalculateTotalCost(self.sol)
        # debuggingOnly
        if abs((newCost - oldCost) - sm.moveCost) > 0.0001:
            print('Cost Issue')


    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm):
            sm.positionOfFirstRoute = firstRouteIndex
            sm.positionOfSecondRoute = secondRouteIndex
            sm.positionOfFirstNode = firstNodeIndex
            sm.positionOfSecondNode = secondNodeIndex
            sm.costChangeFirstRt = costChangeFirstRoute
            sm.costChangeSecondRt = costChangeSecondRoute
            sm.moveCost = moveCost

    # VND

    def VND(self):
        self.bestSolution = self.cloneSolution(self.sol)
        VNDIterator = 0
        kmax = 1
        rm = RelocationMove()
        sm = SwapMove()
        
        k = 1
        draw = True

        while k <= kmax:
            self.InitializeOperators(rm, sm)
            
            if k == 1:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None and rm.moveCost < 0:
                    self.ApplyRelocationMove(rm)
                    if draw:
                        SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.cost)
                    
                    k = 1
                else:
                    k += 1
            """
            elif k == 2:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None and sm.moveCost < 0:
                    self.ApplySwapMove(sm)
                    if draw:
                        SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.cost)
                    k = 1
                else:
                    k += 1
            """
            
                
            if (self.sol.cost < self.bestSolution.cost):
                self.bestSolution = self.cloneSolution(self.sol)

        SolDrawer.draw('final_vnd', self.bestSolution, self.allNodes)
        SolDrawer.drawTrajectory(self.searchTrajectory)