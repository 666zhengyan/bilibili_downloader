import os
import time
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright
import asyncio
import LOGIN
import aiohttp
import re
import video
from concurrent.futures import ProcessPoolExecutor
import tools
import subprocess
import requests
from tqdm import tqdm
import threading
#视频的名字在页面源代码里面，用正则匹配Phone_video_title__8fHdx
class get_VIP_video(LOGIN.Login):
    headers = None
    GPU=None
    save_path=None
    tqdm=None
    #维护一个video对象列表，里面每一个对象就是一个视频以及它对应的所有信息
    video_obj_list=[]
    def __init__(self,**kwargs):
        self.urllist=kwargs.get('urllist',[])
        self.GPU=kwargs.get('GPU',False)
        self.save_path=kwargs.get('save_path','D:')
        self.broswerType = kwargs.get('broswerType', 'msedge')
        LOGIN.Login.__init__(self,**kwargs)

    async def get_the_vip(self, url):
        temp_obj = video.video()
        async def func(route):
            # print("抓到了")
            url = route.request.url
            headers = route.request.headers
            self.headers = headers
            async with aiohttp.ClientSession() as f:
                response = await f.get(headers=headers, url=url)
                myjson = await response.json()
                video_url = myjson['result']['video_info']['dash']['video'][0]['baseUrl']
                audio_url = myjson['result']['video_info']['dash']['audio'][0]['baseUrl']
                temp_obj.set1(video_url=video_url, audio_url=audio_url)
        #每个页面都会生成一个video对象保存视频音频的所有信息
        own_page = await self.context.new_page()
        await own_page.route('https://api.bilibili.com/pgc/player/web/v2/playurl**', func)
        await own_page.goto(url,timeout=60000)
        await asyncio.sleep(2)
        #获取视频名字
        async with aiohttp.ClientSession() as f:
            response = await f.get(url=url, headers=self.headers)
            text=await response.text()
            pattern=re.compile('div class="Phone_video_title__8fHdx">(.*?)</div>')
            result=pattern.findall(text)[0]
            # 定义正则表达式，匹配除了字母、数字、下划线、连字符和汉字以外的字符
            pattern = re.compile(r'[^\w\-_\u4e00-\u9fa5]')  # 匹配除了字母、数字、下划线、连字符和汉字以外的字符
            # 使用正则表达式进行替换
            output_string = pattern.sub('_', result)
            temp_obj.set2(video_name=output_string+'.m4s',headers=self.headers,save_path=self.save_path)
            self.video_obj_list.append(temp_obj)
        

    async def main(self):
        async with async_playwright() as p:
            await super().login(p)
            # 异步执行多个任务,开启多个页面
            task = []
            for i in self.urllist:
                task.append(asyncio.create_task(self.get_the_vip(i)))
            result = await asyncio.gather(*task)
            await self.browser.close()

    def run(self):
        #异步打开页面，获得视频的所有信息
        asyncio.run(self.main())

#传入一个video对象，然后将该对象内的小片段内容全部下载
async def download(obj_video,wrong_list):
    tasks=[]
    session=aiohttp.ClientSession()
    mybar=tqdm(desc='下载进度',total=len(obj_video.little_video_list)+len(obj_video.little_audio_list))
    for i in obj_video.little_video_list:
        tasks.append(asyncio.create_task(video.dowmload(i,session,mybar,wronglist=wrong_list)))
    for j in obj_video.little_audio_list:
        tasks.append(asyncio.create_task(video.dowmload(j,session,mybar,wronglist=wrong_list)))

    result=await asyncio.gather(*tasks)
    await session.close()


def run(obj_video,wrong_list):
    asyncio.get_event_loop().run_until_complete(download(obj_video,wrong_list))
    print('下载失败的数量：',len(wrong_list))

   #对于下载失败的情况还需要改进，流式下载
    bar=tqdm(total=len(wrong_list),desc="重新下载失败的分片")
    for i in wrong_list:
        try:
            headers = i.headers
            headers['Range'] = f'bytes={i.start_range}-{i.right}'
            response = requests.get(url=i.url, headers=headers)
            if response.status_code!=206:
                raise Exception
            with open(f'{i.name}', 'wb') as f:
                f.write(response.content)
                bar.update()
        except Exception as e:
            print('发生错误')
            for j in range(10):
                time.sleep(2)
                try:
                    headers = i.headers
                    headers['Range'] = f'bytes={i.start_range}-{i.right}'
                    response = requests.get(url=i.url, headers=headers)
                    if response.status_code!=206 or (response.headers['Content-Length']!=1024000 and i.start_range<i.right):
                        raise Exception
                    with open(f'{i.name}', 'wb') as f:
                        f.write(response.content)
                except:
                    continue
                else:
                    print("重新下载成功")
                    bar.update()
                    break


    with open(f'video-{obj_video.video_name}','ab+') as f:
        for i in obj_video.little_video_list:
            with open(f'{i.name}', 'rb') as p:
                f.write(p.read())


    with open(f'audio-{obj_video.video_name}','ab+') as f:
        for i in obj_video.little_audio_list:
            with open(f'{i.name}', 'rb') as p:
                f.write(p.read())


    tools.merge_m4s_to_mp4(input_files=[f'video-{obj_video.video_name}',f'audio-{obj_video.video_name}'], output_file=f'{obj_video.video_name}'.replace('.m4s','.mp4'), GPU=True,save_path=obj_video.save_path)
def execute(obj_get_VIP_video):
    with ProcessPoolExecutor(max_workers=5) as f:
        for i in obj_get_VIP_video.video_obj_list:
            #每个进程都将维护一个下载失败列表
            wrong_list=[]
            f.submit(run,i,wrong_list)
    #tools.remove_files(r'D:\pythonProject\bilibili','.m4s')


if __name__=="__main__":
    climb = get_VIP_video(urllist=[
       'https://www.bilibili.com/bangumi/play/ep4141?spm_id_from=333.337.0.0',
        'https://www.bilibili.com/bangumi/play/ep4140?spm_id_from=333.337.0.0&from_spmid=666.25.episode.0',
        'https://www.bilibili.com/bangumi/play/ep4139?spm_id_from=333.337.0.0&from_spmid=666.25.episode.0'
    ],
        GPU=True, save_path=r'D:\保存下载的视频',broswerType='msedge')
    climb.run()
    execute(climb)
    tools.remove_files(os.path.dirname(os.path.abspath(__file__)), '.m4s')
