import asyncio
from playwright.async_api import async_playwright
import os
class Login:
    browser=None
    page=None
    context=None

    def __init__(self,**kwargs):
        self.broswerType=kwargs.get('broswerType','msedge')


    async def login(self,playwright):
        chromium = playwright.chromium  # or "firefox" or "webkit".
        self.browser = await chromium.launch(channel=self.broswerType,headless=False)
        if os.path.exists('cookie.json'):
            self.context = await self.browser.new_context(storage_state="cookie.json")
        else:
            self.context = await self.browser.new_context()

        self.page = await self.context.new_page()
        await self.page.goto("https://www.bilibili.com/",timeout=60000)
        """
        我需要代码在这里阻塞，直到用户完成登录操作为止
        用pause似乎有点傻
        """
        if os.path.exists('cookie.json')==False:
            await self.page.pause()
            await self.context.storage_state(path="cookie.json")

    async def main(self):
        async with async_playwright() as p:
            await self.login(p)
            await self.browser.close()

    def run(self):
        asyncio.run(self.main())

if __name__=="__main__":
    login=Login()
    login.run()




