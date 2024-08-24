from typing import Optional, List, Any, Coroutine

from sqlmodel import Field, select

from gsuid_core.utils.database.base_models import BaseModel
from gsuid_core.webconsole.mount_app import PageSchema, GsAdminModel, site


# 创建类时传参带上`table=True`才是建表，否则只是Python内部的类继承，不会实际建立表格
class WeatherBind(BaseModel, table=True):
    city_name: Optional[str] = Field(default=None, title='城市名称')
    city_code: Optional[int] = Field(default=None, title='城市编码')
    sub_warn: Optional[bool] = Field(default=False, title='是否订阅预警')
    sub_forecast: Optional[bool] = Field(default=False, title='是否订阅预报')
    push: Optional[bool] = Field(default=False, title='是否开启推送')

    # 获取用户绑定的城市列表
    @classmethod
    async def get_user_city(
        cls,
        user_id: str,
        bot_id: str,
    ) -> Optional:
        """获取用户绑定的城市列表"""
        data = await cls.select_data(user_id=user_id, bot_id=bot_id)
        return data

    # 绑定
    @classmethod
    async def bind_user_city(cls, user_id: str, bot_id: str, data=dict) -> None:
        await cls.insert_data(user_id=user_id, bot_id=bot_id, **data)



# 注册网页控制台的类
@site.register_admin
class WeatherBindadmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(
        label='天气绑定管理',
        icon='fa fa-users',
    )  # type: ignore

    # 配置管理模型
    model = WeatherBind
