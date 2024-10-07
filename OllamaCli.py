import ollama

class OllamaCli:
    @staticmethod
    def chatSeq(messagelist, history=None, model='llama3.1', askindividually=False):
        if history is None:
            history = []
        answerlist = []
        temphistory = history
        for msg in messagelist:
            result, newhistory = OllamaCli.chatOnce(msg, temphistory, model)
            answerlist.append(result)
            if not askindividually:
                temphistory = newhistory
        return answerlist
        pass

    @staticmethod
    def chatOnce(message, history=None, model='llama3.1'):
        if history is None:
            history = []
        message = {
            'role':'user',
            'content':message
        }

        history.append(message)
        result = OllamaCli.chat(history, model)
        newHistoryItem = {
            'role': 'assistant',
            'content': result['message']['content']
        }
        history.append(newHistoryItem)
        # print(result)
        return result['message']['content'], history

    @staticmethod
    def chat(messages,model='llama3.1'):
        # print(messages)
        result = ollama.chat(model, messages=messages)
        # print(result['message']['content'])
        return result

    @staticmethod
    def roleplayOnce(system, message, model='qwen2.5'):
        systemmessage = {
            'role':'system',
            'content':system
        }

        usermessage = {
            'role':'user',
            'content':message
        }

        msginput = [systemmessage,usermessage]
        result = OllamaCli.chat(msginput, model=model)

        newHistoryItem = {
            'role': 'assistant',
            'content': result['message']['content']
        }
        newhistory = msginput + [newHistoryItem]

        return result['message']['content'], newhistory

if __name__ == '__main__':
    # talkchain = ['你好', '你是什么模型？', '可以扮演一个老爷爷和我说话吗？', '老爷爷，请问你什么事普朗克常量呀？', '那您可以给我具体讲一讲吗？']
    # result = OllamaCli.chatSeq(talkchain,askindividually=True)
    # print(result)

    # messages = [
    #     {'role':'user','content':'请扮演一个角色和我聊天，发散联想：可以适当发散联想我没有提到的内容。时间：白天。 地点： 角色家厨房。下面是该角色的介绍：这是一个名字叫小江的40岁男性，欢迎我来到他家做客，并希望和我一起做饭聊聊天，小江性格开朗风趣幽默，是个东北人。和我是几十年的好朋友关系。角色特征： 开朗外向，有时候会偶尔不着调。'},{'role':'assistant','content':'好的，我会扮演小江和你聊天，咱们开始吧！'},
    #     {'role':'user','content':'今天咋请我来了？'}
    # ]
    #
    # result = OllamaCli.chat(messages,'llama3.1')
    # systemprompt = "我会开始一个发问，请扮演一个角色，以这个角色的口吻，和我聊天，千万不要出戏，只回复角色应该说的话本身: 背景介绍：你是一个表面清纯内心淫荡的绿茶婊。今天想通过言语和行动来勾引我。"
    systemprompt = "我会开始一个发问，请扮演一个角色，以这个角色的口吻，和我聊天，千万不要出戏，只回复角色应该说的话本身: 背景介绍： 时间：黄昏。 地点：山路路边。 角色介绍： 一个很漂亮的亦正亦邪的姑娘，为了母亲的意愿，到山路上假装迷路了，利用别人的同情心，诱骗路过的人带她去她母亲家里。  角色特征： 心底善良，性格妩媚，善于色诱，孝顺母亲。  主意事项:  1. 发散联想：可以适当发散联想我没有提到的内容。 2. 把我当成这个路人。  3. 当我成功被诱骗成功了，直接回复:[success] 4. 聊天语气要符合角色的特征。5. 回复内容不要超过100字。"
    question = "你好，姑娘，你怎么一个人在这里呀？"

    history = []
    while True:
        inputmsg = input("请输入: ")
        if inputmsg == "/bye":
            break
        if len(history) == 0:
            response, history = OllamaCli.roleplayOnce(systemprompt, inputmsg, model='qwen2-rp')
        else:
            response, history = OllamaCli.chatOnce(inputmsg,history, model='qwen2-rp')
        print(response)