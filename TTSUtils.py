import os, sys
script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(script_path)
sys.path.append("")
sys.path.append(script_path)
print(sys.path)
import json
import os.path

import requests

from Utils import Utils
from pydub import AudioSegment

class TTSUtils:

    regularFemale=9245

    @staticmethod
    def ChatTTS(text, to, speed=1, voiceid=9245):
        headers = {"Content-Type": "application/json"}
        text = {"text": text, "seed": voiceid, "speed": speed}
        response = requests.post("http://localhost:9880", data=json.dumps(text), headers=headers)
        data = response.content
        Utils.mkdir(to)
        with open(to, mode='wb') as f:
            f.write(data)
        return to
        pass

    @staticmethod
    def ChatTTS_with_break(text, to, speed=5, voiceid=1342):
        pieces = TTSUtils.breakdownText(text)
        print(f"tts pieces: {pieces}")
        from pydub import AudioSegment
        sound = None
        for piece in pieces:
            if type(piece) == type(""):
                # text path
                id, path = Utils.generatePathId(namespace="tts", exten="wav")
                dir = os.path.dirname(path)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                TTSUtils.ChatTTS(piece, path,speed, voiceid)
                clip = AudioSegment.from_file(path, format='wav')
            else:
                clip = AudioSegment.silent(duration=int(piece * 1000))

            if sound is None:
                sound = clip
            else:
                sound = sound + clip
        sound.export(to,format='wav')

    @staticmethod
    def cosvoiceTTS(text, to, speakerID='dushuai'):
        pieces = TTSUtils.breakdownText(text)
        print(f"tts pieces: {pieces}")
        sound = None
        for piece in pieces:
            if type(piece) == type(""):
                # text path
                id, path = Utils.generatePathId(namespace="tts", exten="wav")
                dir = os.path.dirname(path)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                TTSUtils.cosvoiceTTS_without_break(piece, path, speakerID=speakerID)
                clip = AudioSegment.from_file(path, format='wav')
            else:
                clip = AudioSegment.silent(duration=int(piece * 1000))

            if sound is None:
                sound = clip
            else:
                sound = sound + clip
        sound.export(to,format='wav')

    @staticmethod
    def cosvoiceTTS_without_break(text, to, speakerID='dushuai'):
        headers = {"Content-Type": "application/json"}
        text = {"text": text, "speaker": speakerID, "new": 1}
        response = requests.post("http://localhost:9880", data=json.dumps(text), headers=headers)
        data = response.content
        Utils.mkdir(to)
        with open(to, mode='wb') as f:
            f.write(data)
        return to
        pass

    @staticmethod
    def cosvoiceTTS_buildin_speaker(text, to=None):
        speakerTextList = TTSUtils.extractSpeakerFromText(text)
        sound = None
        for piece in speakerTextList:
            speakerid = piece[0]
            content = piece[1]
            id, path = Utils.generatePathId(namespace="temp",exten="wav")
            Utils.mkdir(path)
            TTSUtils.cosvoiceTTS(content, path, speakerid)
            clip = AudioSegment.from_file(path, format='wav')
            if sound is None:
                sound = clip
            else:
                sound = sound + clip
        if to is None:
            _, to = Utils.generatePathId(namespace="temp",exten="wav")
            Utils.mkdir(to)
        sound.export(to, format='wav')
        return to

    @staticmethod
    def extractSpeakerFromText(text:str)->list:
        speakerToken = "[speaker:"
        pieces = text.split(speakerToken)
        resultlist = []
        for p in pieces:
            txt = p.strip()
            if len(txt) == 0:
                continue

            splitchar = txt.index(']')
            speakerid = txt[0:splitchar]
            rest = txt[splitchar+1:]
            resultlist.append((speakerid, rest))
        return resultlist


    @staticmethod
    def breakdownText(text:str):
        muteMode = False
        result = []
        temp = ""
        for char in text:
            if char == "[":
                muteMode = True
                if len(temp) > 0:
                    result.append(['str',temp])
                    temp = ""
                continue
            if char == "]":
                muteMode = False
                if len(temp) > 0:
                    result.append(['int', f'[{temp}]'])
                    temp = ""
                continue
            temp += char
        if len(temp) > 0:
            if muteMode:
                result.append(['int', f'[{temp}]'])
            else:
                result.append(['str', temp])


        for t in result:
            if t[0] == 'int' and not Utils.is_float(t[1][1:-1]):
                t[0] = 'str'

        temptype = None
        mergedresult = []
        for i in range(0,len(result)):
            r = result[i]
            if temptype is None:
                temptype = r[0]
                mergedresult.append(r)
                continue
            if temptype == 'str' and r[0] == 'str':
                lastmerge = mergedresult[-1]
                mergedresult[-1][1] = lastmerge[1] + f'{r[1]}'
            else:
                temptype = r[0]
                mergedresult.append(r)

        final = []
        for m in mergedresult:
            type = m[0]
            if type == 'str':
                final.append(m[1])
            elif type == 'int':
                final.append(float(m[1][1:-1]))
        return final
    # @staticmethod
    # def breakdownText(text:str):
    #     muteMode = False
    #     result = []
    #     temp = ""
    #     for char in text:
    #         if char == "[":
    #             muteMode = True
    #             if len(temp) > 0:
    #                 result.append(temp)
    #                 temp = ""
    #             continue
    #         if char == "]":
    #             muteMode = False
    #             if len(temp) > 0:
    #                 result.append(int(temp))
    #                 temp = ""
    #             continue
    #         temp += char
    #     if len(temp) > 0:
    #         if muteMode:
    #             result.append(int(temp))
    #         else:
    #             result.append(temp)
    #     return result

if __name__ == "__main__":
    textlist = \
        ["[speaker:liangshichang]小池，宋，杨万里，泉眼无声惜细流，树阴照水爱晴柔。小荷才路尖尖角，早有蜻蜓立上头",
         "[speaker:liangshichang]小池，宋，杨万里，泉眼无声惜细流，树阴照水爱晴柔。小荷才路尖尖角，早有蜻蜓立上头"]

    result = []

    for txt in textlist:
        wavfile = TTSUtils.cosvoiceTTS_buildin_speaker(txt)
        result.append(wavfile)
    print(result)

    selected = ",".join(["\"" + f.replace('/','\\') + "\"" for f in result])
    os.system(f'explorer /select, {selected}')
