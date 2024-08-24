# 先导入基础配置模型
from typing import Dict

# 导包
from gsuid_core.data_store import get_res_path

# 然后添加到GsCore网页控制台中
from gsuid_core.utils.plugins_config.gs_config import StringConfig
from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsStrConfig,
)

# 建立自己插件的CONFIG_DEFAULT
# 名字无所谓, 类型一定是Dict[str, GSC]，以下为示例，可以添加无数个配置
CONIFG_DEFAULT: Dict[str, GSC] = {
    'key': GsStrConfig(
        'Key',  # 这个是该配置的名称
        '申请地址：https://dev.qweather.com/docs/',  # 这个是该配置的详细介绍
        '',  # 这个是该配置的默认参数，这里我们直接为空即可
    ),
}

# 设定一个配置文件（json）保存文件路径
# 这里get_res_path()的作用是定位到 gsuid_core/data路径下
CONFIG_PATH = get_res_path('Weather') / 'config.json'

# 上面的路径为 gsuid_core/data/Gs_Weather/config.json

# 分别传入 配置总名称（不要和其他插件重复），配置路径，以及配置模型
tq_config = StringConfig('Weather', CONFIG_PATH, CONIFG_DEFAULT)
