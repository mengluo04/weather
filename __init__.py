from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from .database import WeatherBind
from .config import tq_config
# 导入httpx的网络请求模块
import httpx

gs_weather_info = SV('天气信息查询')

# 在这里填入你自己的KEY码，在Python中，字符串使用单引号，双引号，三引号都可以。
KEY = tq_config.get_config('key').data


# 这里我们额外添加一个触发器`on_suffix`，这个触发器用于在末尾触发命令
# 加上之后，该触发器会响应用户的`漳州天气`指令，而不是只响应`天气漳州`
@gs_weather_info.on_suffix('天气', block=True)
@gs_weather_info.on_command('天气', block=True)
async def send_weather_msg(bot: Bot, ev: Event):
    # 获取用户输入的城市，如果为空，做出提醒，并用return中断函数运行
    text = ev.text.strip()
    # 创建一个请求客户端
    client = httpx.AsyncClient()

    # 如果用户没有输入任何参数
    if not text:

        # 进行检查是否有绑定
        data = await WeatherBind.get_user_city(ev.user_id, ev.bot_id)
        # 如果连绑定都没有，则提醒用户
        if data is None:
            return await bot.send('请输入城市名称，或使用 tq绑定城市【城市名称】 命令！')
        # 存在UUID的绑定，则我们进行分割
        # 别忘了我们绑定的时候，UUID的值是 城市名|城市ID
        city_name = data.city_name
        city_code = data.city_code
    # 有输入参数则直接使用用户输入
    else:
        # 根据用户传入的信息，请求城市ID和城市完整名称
        # ev是当前事件的一系列可用信息，例如ev.text就是去除了命令之后的用户输入
        # 例如用户输入 天气漳州 ，ev.text = 漳州
        # 要获取完整用户输入，ev.raw_text = 天气漳州，ev.command = 天气
        pos_resp = await client.get(
            'https://geoapi.qweather.com/v2/city/lookup',
            params={
                'location': text,
                'key': KEY,
            },
        )
        # 解析结果为pyhon中的字典
        pos_data = pos_resp.json()
        # 获取结果中的响应代码
        pos_retcode = pos_data['code']

        # 响应码不为200则发生了报错，我们把错误码返回给用户，便于定位错误信息
        if pos_retcode != '200':
            await bot.send(f'[天气] 获取天气信息失败！错误码为 {pos_retcode}')
        else:
            # 城市ID，就是要用这个ID请求下面的天气信息
            city_code = pos_data['location'][0]['id']
            city_name = pos_data['location'][0]['name']

    # 再进行一次请求
    weather_resp = await client.get(
        'https://devapi.qweather.com/v7/weather/now',
        params={
            'location': city_code,
            'key': KEY,
        },
    )

    weather_data = weather_resp.json()
    weather_retcode = weather_data['code']

    # 错误码处理"
    if weather_data['code'] != '200':
        await bot.send(
            f'[天气] 获取天气信息失败！错误码为 {weather_retcode}！'
        )
    else:
        # 现在温度
        now_temp = weather_data['now']['temp']
        # 湿度
        now_hum = weather_data['now']['humidity']
        # 现在的体感温度
        now_feels = weather_data['now']['feelsLike']
        # 天气
        now_text = weather_data['now']['text']

        # 将结果进行字符串拼贴，便于把最后的结果呈现给用户
        text = (f'{city_name}现在的天气是：{now_text}\n'
                f'温度：{now_temp} 度\n'
                f'湿度：{now_hum} %\n'
                f'体感温度为: {now_feels} 度'
                )

        await bot.send(text)


@gs_weather_info.on_command('tq绑定城市')
async def bind_city(bot: Bot, ev: Event):
    # 获取用户输入的城市，如果为空，做出提醒，并用return中断函数运行
    text = ev.text.strip()
    if not text:
        return await bot.send('请输入城市名称！')

    # 进行一次请求，我们只需要存储最后的城市ID即可
    client = httpx.AsyncClient()
    pos_resp = await client.get(
        'https://geoapi.qweather.com/v2/city/lookup',
        params={
            'location': text,
            'key': KEY,
        },
    )

    pos_data = pos_resp.json()
    pos_retcode = pos_data['code']

    # 如果根据用户输入，无法找到对应城市，则发出提醒
    if pos_retcode != '200':
        return await bot.send('你输入的城市不存在, 请检查输入是否有误!')
    else:
        # 获取城市ID
        city_code = pos_data['location'][0]['id']
        city_name = pos_data['location'][0]['name']

        # 然后把处理后的数据插入数据库，和UserID相对应
        # 这个内置函数可以接受多个ID的插入，方便后续多绑定
        await WeatherBind.bind_user_city(
            ev.user_id, ev.bot_id, {'city_code': city_code, 'city_name': city_name}
        )
        return await bot.send(f'绑定城市 {city_name} 成功！')
