import json
import os.path
import sys

script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(script_path)
sys.path.append("")
sys.path.append(script_path)
print(sys.path)
from ImmortalEntity import ImmortalEntity
from keywords import ContextKeyword
import Events



class ImmortalPlayer:
    @staticmethod
    def Play(packageDir, nodeid=None, contextDict=None):
        configfile = os.path.join(packageDir, 'entity.json')
        with open(configfile, 'r', encoding='utf-8') as f:
            configStr = f.read()
        jsConfig = json.loads(configStr)
        properties = jsConfig["Properties"]
        nodes = jsConfig["Nodes"]


        # init new context
        newContext = {}
        if contextDict is None or len(contextDict.keys()) == 0:
            newContext = {ContextKeyword.bgmkey: "", ContextKeyword.nodewalkcount: 0}
        else:
            newContext = contextDict

        newContext = ImmortalPlayer.updateContext(newContext)
        newContext = ImmortalPlayer.handleOnLeave(jsConfig, newContext)

        if nodeid is None:
            newNodeId = properties["root"]
        else:
            newNodeId = nodeid
            # node = ImmortalEntity.getNodeById(jsConfig, nodeid)
            # nextList = ImmortalEntity.searchNextNodes(jsConfig, nodeid,newContext)


        node = ImmortalEntity.getNodeById(jsConfig, newNodeId)

        # handle events
        newContext = ImmortalPlayer.handleOnEnter(jsConfig, node, newContext)

        nextList = ImmortalEntity.searchNextNodes(jsConfig, newNodeId, newContext)

        return node, {"data": nextList}, newContext

    @staticmethod
    def handleOnLeave(entity, newContext:dict):
        lastNodeid = None
        if newContext.keys().__contains__(ContextKeyword.currentnodeid) and newContext[ContextKeyword.currentnodeid] is not None:
            lastNodeid = newContext["lastnode"]
        if lastNodeid is not None and len(lastNodeid) > 0:
            print(f"last node id : {len(lastNodeid)}")
            # handle last node on leave event
            lastnode = ImmortalEntity.getNodeById(entity, lastNodeid)
            events = lastnode["Events"]
            onleavekey = "Onleave"
            if events.keys().__contains__(onleavekey):
                onleave:dict = events[onleavekey]
                newContext = Events.EventHandler.handleEvent(newContext, onleave)
        #
        # if node is not None:
        #     events:dict = node["Events"]
        #     onenterkey = "OnEnter"
        #     if events.keys().__contains__(onenterkey):
        #         onenter:dict = events[onenterkey]
        #         newContext = Events.EventHandler.handleEvent(newContext, onenter)

        return newContext
        pass
    @staticmethod
    def handleOnEnter(entity, node, newContext:dict):
        print(f"on enter start: node: {node}, new context: {newContext}")
        lastNodeid = None
        if newContext.keys().__contains__(ContextKeyword.currentnodeid) and newContext[ContextKeyword.currentnodeid] is not None:
            lastNodeid = newContext["lastnode"]
        # if lastNodeid is not None:
        #     # handle last node on leave event
        #     lastnode = ImmortalEntity.getNodeById(entity, lastNodeid)
        #     events = lastnode["Events"]
        #     onleavekey = "Onleave"
        #     if events.keys().__contains__(onleavekey):
        #         onleave:dict = events[onleavekey]
        #         newContext = Events.EventHandler.handleEvent(newContext, onleave)

        if node is not None:
            events:dict = node["Events"]
            onenterkey = "OnEnter"
            if events.keys().__contains__(onenterkey):
                onenter:list = events[onenterkey]
                newContext = Events.EventHandler.handleEvent(newContext, onenter)

        return newContext
        pass

    pass

    @staticmethod
    def updateContext(newContext):
        traversed = 0
        if newContext.keys().__contains__(ContextKeyword.nodewalkcount):
            traversed = newContext[ContextKeyword.nodewalkcount]
        newContext.setdefault(ContextKeyword.nodewalkcount, traversed+1)
        return newContext
        pass


if __name__ == "__main__":
    args = sys.argv
    fpackageDir = args[1]
    fnodeid = args[2]
    fcontextDict = args[3]

    # outputs
    onode = args[4]
    onextlist = args[5]
    onewContext = args[6]

    with open(fpackageDir) as f:
        packageDir = f.read()
    with open(fnodeid) as f:
        nodeid = f.read()
        if len(nodeid) == 0:
            nodeid = None
    with open(fcontextDict) as f:
        contextDict = json.loads(f.read())

    node, nextList, newContext = ImmortalPlayer.Play(packageDir, nodeid, contextDict)

    onodedir = os.path.dirname(onode)
    onextlistdir = os.path.dirname(onextlist)
    onewContextdir = os.path.dirname(onewContext)

    if not os.path.exists(onodedir):
        os.makedirs(onodedir)
    if not os.path.exists(onextlistdir):
        os.makedirs(onextlistdir)
    if not os.path.exists(onewContextdir):
        os.makedirs(onewContextdir)

    with open(onode, 'w') as f:
        jsn = json.dumps(node)
        print("output node:\n")
        print(jsn)
        f.write(jsn)
    with open(onextlist, 'w') as f:
        jsn = json.dumps(nextList)
        print("output next list: ")
        print(jsn)
        f.write(jsn)
    with open(onewContext, 'w') as f:
        jsn = json.dumps(newContext)
        print("output new context: ")
        print(jsn)
        f.write(jsn)
