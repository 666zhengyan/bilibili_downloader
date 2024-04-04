"""
这个python文件相当重要，其中video类是用来沟通
各个部分的关键类，还有关键的异步下载函数，这个函数需要完成分割
任务以及按照正确顺序拼接文件，另外还有一个转码的函数
"""
import asyncio
import requests
import aiofiles

class video:
    #注意类变量与实例变量
    #视频文件最后保存的名字
    video_name=None
    video_url=None
    audio_url=None
    #视频文件最后保存的位置
    save_path=None
    headers=None
    #维护一个分别包含视频小片段和音频小片段对象的列表
    # little_video_list=[]
    # little_audio_list=[]

    def __init__(self):
        self.little_video_list = []
        self.little_audio_list = []


    def set1(self,**kwargs):
        self.video_url = kwargs.get('video_url', None)
        self.audio_url = kwargs.get('audio_url', None)


    def set2(self,**kwargs):
        self.video_name = kwargs.get('video_name', None)
        self.headers = kwargs.get('headers', None)
        self.save_path=kwargs.get('save_path','D:')
        self.update()

    #更新两个列表
    def update(self):
        video_length=get_length(self.video_url,self.headers)
        #print(video_length)
        #print(video_length)
        audio_length=get_length(self.audio_url,self.headers)
        #print(audio_length)
        block_size=1024000
        left=0
        right=min(left+block_size-1,int(video_length))
        while True:
            if left>int(video_length):
                break
            the_little_video_obj=little_video(name=str(left)+'-'+str(right)+'video'+self.video_name,start_range=left,size=block_size,headers=self.headers,url=self.video_url,right=right)
            self.little_video_list.append(the_little_video_obj)
            left=right+1
            right = min(left + block_size-1, int(video_length))

        left = 0
        right = min(left + block_size-1, int(audio_length))
        while True:
            if left>int(audio_length):
                break
            the_little_video_obj=little_video(name=str(left)+'-'+str(right)+'audio'+self.video_name,start_range=left,size=block_size,headers=self.headers,url=self.audio_url,right=right)
            self.little_audio_list.append(the_little_video_obj)
            left=right+1
            right = min(left + block_size-1, int(audio_length))

#这个类需要保存异步分块下载的每一个小文件信息
class little_video:
    #文件名字
    name=None
    #在原文件中的起始位置和结束位置
    start_range=None
    right=None
    #大小
    size=None
    headers = None
    url=None
    #是否完成下载标志
    have_done=False
    def __init__(self,**kwargs):
        self.name=kwargs.get('name',None)
        self.start_range=kwargs.get('start_range',None)
        self.right=kwargs.get('right',None)
        self.size=kwargs.get('size',None)
        self.headers = kwargs.get('headers', None)
        self.url=kwargs.get('url',None)
        self.have_done=kwargs.get('have_done',False)


def get_length(url,headers):
    response = requests.head(url=url, headers=headers).headers
    return response.get('Content-Length')

async def dowmload(OBJ_little_video,session,bar,wronglist):
    headers=OBJ_little_video.headers
    headers['Range']=f'bytes={OBJ_little_video.start_range}-{OBJ_little_video.right}'
    try:
        async with session.get(url=OBJ_little_video.url, headers=headers) as r:
            response = await r.read()
            if r.status != 206:
                raise Exception('响应码不是206')
            if int(r.headers['Content-Length']) < 1024000 and OBJ_little_video.start_range < OBJ_little_video.right:
                raise Exception('响应的数据不正确')
    except Exception as e:
        print(str(e))
        wronglist.append(OBJ_little_video)
    else:
        async with aiofiles.open(f'{OBJ_little_video.name}', 'ab') as f:
            await f.write(response)
        OBJ_little_video.have_done = True
        bar.update()


