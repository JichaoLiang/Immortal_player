import json
import os.path
import shutil
from abc import abstractmethod

from keywords import ContextKeyword
from keywords import EntityKeyword
import ImmortalEntity
from Utils import Utils
from OllamaCli import OllamaCli
from TTSUtils import TTSUtils
from Wav2lipCli import Wav2lipCli
from MovieMakerUtils import MovieMakerUtils
from ImmortalAgent import ImmortalAgent
from ImmortalPlayer import ImmortalPlayer

class IAction:
    @abstractmethod
    def handleRequest(self, packageDir, packageEntity, actionNode:dict, nextList:list, context:dict):
        pass

# 默认实时回话场景
class DefaultChatAction(IAction):
    packageDir = ''
    def getVideopathById(self, id):
        return os.path.join(self.packageDir,'videos', f"{id}.mp4")

    def handleRequest(self, packageDir, packageEntity, actionNode:dict, nextList:list, context:dict):
        self.packageDir = packageDir
        history = []
        historykey_context = f"{ContextKeyword.DefaultChatAction_history}_{actionNode['ID']}"
        if context.keys().__contains__(historykey_context):
            history = context[historykey_context]
        datafield = ImmortalEntity.ImmortalEntity.getDataField(actionNode)
        prompt = datafield["Prompt"]
        print(f'prompt: {prompt}')
        promptHistory = json.loads(prompt)
        wholehistory = promptHistory + history
        videotemplate = datafield["VideoTemplateList"]
        defaultvideo = actionNode["VideoDataKey"]

        datafield = ImmortalEntity.ImmortalEntity.getDataField(actionNode)
        keywordmappingfield = []
        if datafield.keys().__contains__(EntityKeyword.ActionKeywordMapping):
            keywordmappingfield = datafield[EntityKeyword.ActionKeywordMapping]
        voiceid = datafield[EntityKeyword.voiceId][EntityKeyword.voiceId]
        question = None
        if context.keys().__contains__(ContextKeyword.Question):
            question = context[ContextKeyword.Question]
            context[ContextKeyword.Question] = ""
        if question is None or len(question) == 0:
            videoFileID = defaultvideo
            datafield["playvideo"] = videoFileID
        else:
            # random pick video template
            picked = Utils.randomPick(len(videotemplate))
            videoFile = self.getVideopathById(videotemplate[picked])
            videoFileID = os.path.basename(videoFile)

            # get response text
            response, newHistory = OllamaCli.chatOnce(question,wholehistory,model='qwen2-rp')
            context[historykey_context] = newHistory[len(promptHistory):]

            #check keyword mapping
            for item in keywordmappingfield:
                key = item["key"]
                value = item["value"]
                # key matched
                if response.__contains__(key) and len(response) < len(key) * 2:
                    # clear history talk in case enter this action again
                    context[historykey_context] = []
                    context[ContextKeyword.Question] = ""
                    return ImmortalPlayer.playNode(packageDir,value,context)
            # TTS
            toid, topath = Utils.generatePathId(namespace="temp", exten="wav")
            TTSUtils.cosvoiceTTS(response, topath, voiceid)

            # generate dhlive
            if not Wav2lipCli.videocheckpointExists(videoFileID):
                print(videoFile)
                print(f'no checkpoint for {videoFileID}, generate one.')
                Wav2lipCli.dh_live_make_checkpoint(videoFile)
            vtoid, vtopath = Utils.generatePathId(namespace="videogen")
            vtopath = os.path.join(packageDir, 'videos', vtoid + ".mp4")

            print(f'vtopath: {vtopath}')
            Wav2lipCli.dh_live(topath,videoFileID,vtopath)

            #pack entity
            datafield["playvideo"] = vtoid
        return actionNode,nextList,context

        pass


# 默认实时回话场景
class ImageChatAction(IAction):
    packageDir = ''
    def getImagepathById(self, id):
        return os.path.join(self.packageDir,'images', f"{id}.png")

    def handleRequest(self, packageDir, packageEntity, actionNode: dict, nextList: list, context: dict):
        self.packageDir = packageDir
        history = []
        historykey_context = f"{ContextKeyword.DefaultChatAction_history}_{actionNode['ID']}"
        if context.keys().__contains__(historykey_context):
            history = context[historykey_context]
        datafield = ImmortalEntity.ImmortalEntity.getDataField(actionNode)
        prompt = datafield["Prompt"]
        print(f'prompt: {prompt}')
        promptHistory = json.loads(prompt)
        wholehistory = promptHistory + history
        videotemplate = datafield["ImageTemplateList"]
        defaultvideo = actionNode["VideoDataKey"]

        datafield = ImmortalEntity.ImmortalEntity.getDataField(actionNode)
        voiceid = datafield[EntityKeyword.voiceId][EntityKeyword.voiceId]
        question = None
        if context.keys().__contains__(ContextKeyword.Question):
            question = context[ContextKeyword.Question]
            context[ContextKeyword.Question] = ""
        if question is None or len(question) == 0:
            videoFileID = defaultvideo
            datafield["playvideo"] = videoFileID
        else:
            # random pick video template
            picked = Utils.randomPick(len(videotemplate))
            imageFile = self.getImagepathById(videotemplate[picked])

            # get response text
            response, newHistory = OllamaCli.chatOnce(question, wholehistory, model='qwen2-rp')
            context[historykey_context] = newHistory[len(promptHistory):]

            # TTS
            toid, topath = Utils.generatePathId(namespace="temp", exten="wav")
            TTSUtils.cosvoiceTTS(response, topath, voiceid)

            MovieMakerUtils.resamplewav(topath, 22050)
            duration = MovieMakerUtils.get_wav_duration(topath)

            vtoid, vtopath = Utils.generatePathId(namespace="videogen",exten="mp4")
            MovieMakerUtils.imageToVideo(imageFile, duration=duration, to=vtopath)

            print(f'vtopath: {vtopath}')
            id, generatedPath = ImmortalAgent.replaceAudio(vtopath, topath)
            vtopath = os.path.join(packageDir, 'videos', vtoid + ".mp4")
            shutil.move(generatedPath, vtopath)

            # pack entity
            datafield["playvideo"] = vtoid
        return actionNode, nextList, context
        pass

ActionMapping = {
    "DefaultFreeChat": DefaultChatAction,
    "DefaultImageFreeChat": ImageChatAction
}