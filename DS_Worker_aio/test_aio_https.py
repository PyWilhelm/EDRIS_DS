import aiohttp
import ssl
import asyncio as aio

@aio.coroutine
def enter_heartbeat():
    sslcontext = ssl.create_default_context(cafile='host.crt')
    conn = aiohttp.TCPConnector(ssl_context=sslcontext)
    session = aiohttp.ClientSession(connector=conn)
    r = yield from session.get('https://localhost:800/test')
    print((yield from r.read()))
    
    
    
    
def main():
    global loop
    loop = aio.ProactorEventLoop()
    aio.set_event_loop(loop)
    loop.run_until_complete(enter_heartbeat())
    #aio.get_event_loop().run_until_complete(enter_heartbeat())
main()