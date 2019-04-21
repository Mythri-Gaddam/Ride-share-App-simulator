import sys
import collections


class inputParams(object):
    def __init__(self):
        self.day = 0
        self.roommate = 0
        self.rpl = collections.OrderedDict()
        self.neighborList = collections.OrderedDict()
        self.regionsPicked = []
        self.maxDepth = 0
        self.profitValues = collections.OrderedDict()

    def parseInputFile(self, filename):
        with open(filename, 'r') as fp:
            for linenum, line in enumerate(fp, 0):
                line = line.strip("\r\n")

                if (linenum == 0):
                    if (line.lower() == "today" or (line.lower() == "yesterday")):
                        self.day = line.lower()

                if (linenum == 1):
                    if (line.lower() == "R1".lower() or (line.lower() == "R2".lower())):
                        self.roommate = line.lower()

                if (linenum == 2):
                    tmp = line.split('),')
                    for tp in tmp:
                        a, b = tp.strip('()').split(',')
                        self.rpl[a] = int(b)

                if (linenum == 3):
                    for k in self.rpl:
                        row = line.strip("[]\r\n")
                        adj = []
                        for x in row.split(','):
                            adj.append(int(x))
                        self.neighborList[k] = adj
                        line = fp.next()
                    for x in line.strip("\r\n").split(','):
                        self.regionsPicked.append(x)

                if (linenum == 4):
                    self.maxDepth = int(line)
                    if (self.day == "today"):
                        for a, b in self.rpl.items():
                            self.profitValues[a] = b
                    else:
                        num_of_regions = len(self.rpl)
                        rpl_sum = sum(self.rpl.values())
                        for (a, b) in self.rpl.items():
                            self.profitValues[a] = int(round(0.5 * ((rpl_sum / num_of_regions) + b)))
        return


class Node(object):

    def __init__(self, r, u):
        self.region = r
        if (r == '*'):
            self.depth = -1
        else:
            self.depth = 0
        self.uv = u
        self.parent = self
        self.children = []
        self.visited = [r]

    def addChild(self, node):
        node.parent = self
        node.depth = self.depth + 1
        node.uv = node.uv + self.getParent().uv
        self.children.append(node)
        node.visited.extend(self.visited)

    def getParent(self):
        return self.parent

    def getChildren(self):
        return self.children

    def getVisited(self):
        return self.visited


class Tree(object):
    def __init__(self, sn):
        self.startNode = sn

    def getStartNode(self):
        return self.startNode


def writeToOutput(nextRegion, utilityValueList):
    with open('output.txt', 'w') as file:
        file.write("%s\n" % nextRegion)
        file.write("%s" % utilityValueList)


def treeTraversal(node, searchPaths):
    if (len(node.getChildren()) == 0):
        path = (node.uv, node.getParent().uv, node.getVisited())
        searchPaths.append(path)
    else:
        for n in node.getChildren():
            treeTraversal(n, searchPaths)


def treeTraversalAtDepth(node, uvl, depth):
    if (node.depth == depth):
        uvl.append(node.uv)
    else:
        for n in node.getChildren():
            treeTraversalAtDepth(n, uvl, depth)


def processReturn(gameTree, myInput):
    # TODO: Compute next region and utility values
    #    print "Processing return"
    # printTree(gameTree);
    node = gameTree.startNode
    if (myInput.regionsPicked[0] == '*'):
        playerDepth = 0
    else:
        playerDepth = len(myInput.regionsPicked)

    #    print "PlayerDepth:",playerDepth;
    searchPaths = []
    treeTraversal(node, searchPaths)
    #    print "Num search paths:", len(searchPaths);

    uvl = []
    potentialPaths = []
    potentialMoves = []
    maxValue = 0
    for k in searchPaths:
        path = k[2]
        path = path[::-1]

        if ((playerDepth % 2 == 1) and (len(path) % 2 == 1)) or ((playerDepth % 2 == 0) and (len(path) % 2 == 0)):
            checkValue = k[0]
        else:
            checkValue = k[1]

        uvl.append(checkValue)
        if (maxValue < checkValue):
            maxValue = checkValue
            potentialPaths[:] = []
            potentialPaths.append(path)
        elif (maxValue == checkValue):
            potentialPaths.append(path)
        else:
            pass;

    for p in potentialPaths:
        if p[playerDepth + 1] not in potentialMoves:
            potentialMoves.append(p[playerDepth + 1])

    if (myInput.day == "today"):
        writeToOutput(sorted(potentialMoves)[0], str(uvl).replace(", ", ",").strip("[]"))
    else:
        staleUVL = []
        treeTraversalAtDepth(node, staleUVL, playerDepth)
        writeToOutput(sorted(potentialMoves)[0], str(staleUVL).replace(", ", ",").strip("[]"))
    exit(0)


def printBranches(node):
    for child in node.children:
        print child.parent.region, "->", child.region, child.depth, child.uv
        printBranches(child)


def printTree(gT):
    print "StartNode", gT.getStartNode().region
    printBranches(gT.getStartNode())
    print


def addAllRegionsAsChildren(node, pV):
    for key in pV.keys():
        newNode = Node(key, pV[key])
        node.addChild(newNode)
    return


def initTree(myInput):
    # Initialize tree with start node = '*'
    tempNode = Node('*', 0)
    gameTree = Tree(tempNode)

    # If target depth = 0 end program process return
    if (myInput.maxDepth == 0):
        # game tree for the first move: player can choose anything
        addAllRegionsAsChildren(tempNode, myInput.profitValues)
        processReturn(gameTree, myInput)

    if (myInput.regionsPicked[0] != '*'):
        for k in myInput.regionsPicked:
            if (k != "PASS"):
                newNode = Node(k, myInput.profitValues[k])
            else:
                newNode = Node(k, 0)
            tempNode.addChild(newNode)
            tempNode = newNode

        if (myInput.maxDepth + 1 == len(myInput.regionsPicked)):
            print "Game done"
            exit(0)

    return (gameTree, tempNode)


def getAdjacentRegions(node, myInput):
    nL = []
    regions = myInput.rpl.keys()
    if (node.region == '*'):
        for k in regions:
            nL.append(k)
    elif (node.region == "PASS"):
        return nL
    else:
        neighborList = myInput.neighborList[node.region]
        for j in range(0, len(regions)):
            if (neighborList[j] == 1) and (node.region != regions[j]):
                nL.append(regions[j])
    return nL


def createBranches(currentNode, myInput):
    stack = [currentNode]

    while stack:
        node = stack.pop()
        if (node.region == "PASS") and (node.getParent().region == "PASS"):
            pass;
        elif (node.depth != myInput.maxDepth):
            p = True
            adjList = getAdjacentRegions(node.getParent(), myInput)
            for r in adjList:
                if r not in node.visited:
                    p = False
                    newNode = Node(r, myInput.profitValues[r])
                    node.addChild(newNode)
                    stack.append(newNode)
            # cannot make any more moves
            if (p is True):
                newNode = Node("PASS", 0)
                node.addChild(newNode)
                stack.append(newNode)


myInput = inputParams()
myInput.parseInputFile(sys.argv[2])
# print "Day:",myInput.day;
# print "Roommate:", myInput.roommate;
# print "RPL:",myInput.rpl;
# print "NL:",myInput.neighborList;
# print "RP:",myInput.regionsPicked;
# print "MD:",myInput.maxDepth;

# Step 1: Initialize Game Tree
(gameTree, currentNode) = initTree(myInput)
# print "Next player = ", myInput.roommate, "Player Depth:" ,pD, "Num Leaves",len(leafNodes);
# for i in leafNodes:
#    print i.region,
# print

# Step 2: Add nodes to the tree from adjacency Matrix
createBranches(currentNode, myInput)

# printTree(gameTree);

# Step 3: Tree traversal to calculate output
processReturn(gameTree, myInput)

