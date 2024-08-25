from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from .database import WeatherBind
from .config import tq_config
# 导入httpx的网络请求模块
import httpx

gs_weather_info = SV('天气信息查询')
# 秘钥
KEY = tq_config.get_config('key').data


@gs_weather_info.on_suffix('天气', block=True)
@gs_weather_info.on_fullmatch('天气', block=True)
async def get_weather_noww(bot: Bot, ev: Event):
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
            return await bot.send(at_sender=not ev.is_tome, message='请输入城市名称，或使用 tq绑定城市【城市名称】 命令！')
        city_name = data.city_name
        city_code = data.city_code
    # 有输入参数则直接使用用户输入
    else:
        city_code, city_name = await get_city_code_by_name(text)
        if not city_code:
            return await bot.send(at_sender=not ev.is_tome, message='你输入的城市不存在, 请检查输入是否有误!')
        else:
            city_code = city_code
            city_name = city_name

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
        await bot.send(at_sender=not ev.is_tome, message=f'获取天气信息失败！错误码为 {weather_retcode}！'
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

        await bot.send(at_sender=not ev.is_tome, message=text)


@gs_weather_info.on_suffix('天气预警', block=True)
@gs_weather_info.on_fullmatch('天气预警', block=True)
async def get_weather_warn(bot: Bot, ev: Event):
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
            return await bot.send(at_sender=not ev.is_tome, message='请输入城市名称，或使用 tq绑定城市【城市名称】 命令！')
        city_code = data.city_code
    # 有输入参数则直接使用用户输入
    else:
        city_code, city_name = await get_city_code_by_name(text)
        if not city_code:
            return await bot.send(at_sender=not ev.is_tome, message='你输入的城市不存在, 请检查输入是否有误!')
        else:
            city_code = city_code
            city_name = city_name

    # 再进行一次请求
    weather_resp = await client.get(
        'https://devapi.qweather.com/v7/warning/now',
        params={
            'location': city_code,
            'key': KEY,
        },
    )

    weather_data = weather_resp.json()
    weather_retcode = weather_data['code']

    # 错误码处理"
    if weather_data['code'] != '200':
        await bot.send(at_sender=not ev.is_tome, message=f'获取天气预警信息失败！错误码为 {weather_retcode}！'
                       )
    else:
        ret = []
        for warning_item in weather_data['warning']:
            # 标题
            title = warning_item['title']
            # 内容
            text = warning_item['text']

            # 将结果进行字符串拼贴，便于把最后的结果呈现给用户
            ret.append(f'{title}\n{text}')

        await bot.send(at_sender=not ev.is_tome, message='\n\n'.join(ret))


@gs_weather_info.on_suffix('天气预报', block=True)
@gs_weather_info.on_fullmatch('天气预报', block=True)
async def get_weather_forecast(bot: Bot, ev: Event):
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
            return await bot.send(at_sender=not ev.is_tome, message='请输入城市名称，或使用 tq绑定城市【城市名称】 命令！')
        city_code = data.city_code
        city_name = data.city_name
    # 有输入参数则直接使用用户输入
    else:
        city_code, city_name = await get_city_code_by_name(text)
        if not city_code:
            return await bot.send(at_sender=not ev.is_tome, message='你输入的城市不存在, 请检查输入是否有误!')
        else:
            city_code = city_code
            city_name = city_name

    # 再进行一次请求
    weather_resp = await client.get(
        'https://devapi.qweather.com/v7/weather/3d',
        params={
            'location': city_code,
            'key': KEY,
        },
    )

    weather_data = weather_resp.json()
    weather_retcode = weather_data['code']

    # 错误码处理"
    if weather_data['code'] != '200':
        await bot.send(at_sender=not ev.is_tome, message=f'获取天气预报信息失败！错误码为 {weather_retcode}！'
                       )
    else:
        ret = []
        for day in weather_data['daily']:
            # 日期
            date = day['fxDate']
            # 最低温度
            min_temp = day['tempMin']
            # 最高温度
            max_temp = day['tempMax']

            # 将结果进行字符串拼贴，便于把最后的结果呈现给用户
            ret.append(f'{date}：{min_temp} 度 ~ {max_temp} 度')
        text = '\n'.join(ret)
        await bot.send(at_sender=not ev.is_tome, message=f"{city_name}3日天气预报\n{text}")


@gs_weather_info.on_command('tq绑定城市')
async def bind_city(bot: Bot, ev: Event):
    # 获取用户输入的城市，如果为空，做出提醒，并用return中断函数运行
    text = ev.text.strip()
    if not text:
        return await bot.send(at_sender=True, message='请输入城市名称！')
    [city_code, city_name] = await get_city_code_by_name(text)
    if not city_code:
        return await bot.send(at_sender=not ev.is_tome, message='你输入的城市不存在, 请检查输入是否有误!')
    else:
        await WeatherBind.bind_user_city(
            ev.user_id, ev.bot_id, {'city_code': city_code, 'city_name': city_name}
        )
        return await bot.send(at_sender=not ev.is_tome, message=f'绑定城市 {city_name} 成功！')


# 根据城市名称获取城市id
async def get_city_code_by_name(name: str) -> [str, str]:
    # 进行一次请求，我们只需要存储最后的城市ID即可
    client = httpx.AsyncClient()
    pos_resp = await client.get(
        'https://geoapi.qweather.com/v2/city/lookup',
        params={
            'location': name,
            'key': KEY,
        },
    )

    pos_data = pos_resp.json()
    pos_retcode = pos_data['code']

    # 如果根据用户输入，无法找到对应城市，则发出提醒
    if pos_retcode != '200':
        return [None, None]
    else:
        # 获取城市ID
        city_code = pos_data['location'][0]['id']
        city_name = pos_data['location'][0]['name']
        return city_code, city_name
