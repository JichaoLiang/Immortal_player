import json
import sys
import os

script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(script_path)
sys.path.append("")
sys.path.append(script_path)
print(sys.path)

import Utils
import DBUtils
import OllamaCli
from datetime import datetime

class DanmuManager:
    def __init__(self):
        pass

    def extractDanmu(self, selection, accepttext, fromTime, platform, toProduct):
        tm = int(fromTime) / 1000
        fromtime = datetime.fromtimestamp(tm)
        # print(type(tm))
        db = DBUtils.DBUtils()
        schema = ['id', 'Platform', 'Created', 'Content', 'ToProductID', 'ext']
        sql = f"select idDanmuStream,Created,Content from immortal.danmustream where platform='{platform}' and Created > '{fromtime}' and productid = '{toProduct}' order by Created asc"
        datatable = db.doQuery(sql)
        data = [(dt[1], dt[2]) for dt in datatable]
        result = self.danmuDecision(selection, accepttext, data)
        print(f'decision result: {result}')
        return result
        pass
    pass

    def getIndexIntent(self, selections, content:str)->int:
        temp = content.strip().replace(' ', '')
        if not temp.isdigit():
            return -1
        character = None
        for t in temp:
            if character is None:
                character = t
            elif t != character:
                return -1
        pindex = int(character) - 1
        if pindex >= len(selections) or pindex < -1:
            pindex = -1
        return pindex
        pass

    def danmuItemDecision(self, selection, text)->int:
        indexintent = self.getIndexIntent(selection, text)
        if indexintent >= 0:
            return indexintent
        selectionStrList = []
        i = 0
        for item in selection:
            i = i + 1
            id = item["id"]
            title = item["title"]
            content = item["text"]
            selectionStrList.append(f'{i}. {title}。')
        selectionsStr = "\n".join(selectionStrList)
        prompts = [{
            'role': 'user',
            'content': f"我会给一个短句，请判断这个短句的含义符合以下几个选项中的哪一个：\n {selectionsStr}. \n 要求：1. 只回复选项的序号数字，不要任何其他信息，也不要回复多个序号。 "
                       f"2. 如果该短句不符合任何选项，直接回复：-1。准备好了吗？"
        },{
            'role': 'assistant',
            'content': "准备好了，请提供要分析的句子。"
        },]
        response, _ = OllamaCli.OllamaCli.chatOnce(text, prompts, model='qwen2')

        response = response.strip()

        if response == '-1' or response.isdigit():
            return int(response) - 1
        else:
            return -1
        pass

    def danmuDecision(self, selection, acceptText, data):
        if len(selection) == 1 and not acceptText:
            return {
                "index": 0,
                "text": selection[0]['title'],
                "customIntent": ""
            }
        scorecard = []
        notrecognized = []
        for i in range(0, len(selection)):
            scorecard.append(0)
        for item in data:
            # data schema: created, content
            content = item[1]
            pickedindex = self.danmuItemDecision(selection, content)
            if pickedindex >= 0:
                scorecard[pickedindex] += 1
            else:
                notrecognized.append(content)
        max = 0
        pindex = -1
        for i in range(0, len(scorecard)):
            currentscore = scorecard[i]
            if currentscore > max:
                max = currentscore
                pindex = i
        if max == 0:
            pindex = -1

        text = ""
        if pindex >= 0:
            text = selection[pindex]["title"]

        conclusionText = ""
        if acceptText and len(notrecognized) > 0:
            conclusionText = self.danmuTextConclusion(notrecognized)

        return {
            "index": pindex,
            "text": text,
            "customIntent": conclusionText
        }
        pass

    def danmuTextConclusion(self, notrecognized):
        randompick = True
        if randompick:
            picked = Utils.Utils.randomPick(len(notrecognized))
            return notrecognized[picked]

        prompts = [{
            'role': 'user',
            'content': f"我会给一个短句，请判断这个短句的含义符合以下几个选项中的哪一个：\n {';'.join(notrecognized)}. \n 要求：1. 只回复选项的序号数字，不要任何其他信息，也不要回复多个序号。 "
                       f"2. 如果该短句不符合任何选项，直接回复：-1。准备好了吗？"
        },{
            'role': 'assistant',
            'content': "准备好了，请提供要分析的句子。"
        },]

        i = 0
        reqStr = []
        for nr in notrecognized:
            i += 1
            reqStr.append(f"{i}. {nr}")


        response, _ = OllamaCli.OllamaCli.chatOnce("\n".join(reqStr), prompts, model='qwen2')

        response = response.strip()
        return response
        pass

    def test(self):
        pass

if __name__ == '__main__':
    args = sys.argv
    inputFile = args[1]
    outputFile = args[2]
    with open(inputFile, encoding='utf-8') as f:
        input = json.load(f)
    selection = input["selection"]
    accepttext = input["acceptcustom"]
    fromTime = input["fromTime"]
    platform = input["platform"]
    toProduct = input["toProduct"]
    danmu = DanmuManager()
    # schema { index: xxx, text: xxx }
    decision = danmu.extractDanmu(selection, accepttext, fromTime, platform, toProduct)
    with open(outputFile, 'w') as f:
        json.dump(decision, f)