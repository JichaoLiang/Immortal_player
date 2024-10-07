import os,sys
script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(script_path)
sys.path.append("")
sys.path.append(script_path)
print(sys.path)
from Utils import Utils
from ImmortalPlayer import ImmortalPlayer
import json

if __name__ == '__main__':
    sn = '1727500360049.226'
    fpackage = r'R:/workspace/ImmortalProject/ImmortalProject/ImmortalWebApp/ImmortalWebApp/bin/Debug/net7.0/temp' \
               r'/package_'+sn
    fnodeid = r'R:\workspace\ImmortalProject\ImmortalProject\ImmortalWebApp\ImmortalWebApp\bin\Debug\net7.0\temp' \
              r'\nodeid_'+sn
    fcontext = r'R:\workspace\ImmortalProject\ImmortalProject\ImmortalWebApp\ImmortalWebApp\bin\Debug\net7.0\temp' \
               r'\context_'+sn


    with open(fpackage) as f:
        packageDir = f.read()
    with open(fnodeid) as f:
        nodeid = f.read()
        if len(nodeid) == 0:
            nodeid = None
    with open(fcontext, encoding='utf-8') as f:
        contextDict = json.loads(f.read())
    node, nextList, newContext = ImmortalPlayer.Play(packageDir, nodeid, contextDict)
    print(f'NODE: {node}')
    print(f'NEXT: {nextList}')
    print(f'CONTEXT: {newContext}')