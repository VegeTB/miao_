from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult, MessageChain
from astrbot.api.star import Context, Star, register
from astrbot.api.all import event_message_type, EventMessageType
from astrbot.api.message_components import Plain, Image
import base64
import random
from typing import AsyncGenerator
from .tts_test import generate_audio 
from .ttp import generate_image
from .office import *
import os
from PIL import Image as PILImage, ImageDraw as PILImageDraw, ImageFont as PILImageFont
import matplotlib.font_manager as fm
from .get_song import search_song
import requests
import time
from .file_send_server import send_file
def get_valid_font(font_name, default_font="Arial"):
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    if font_name in available_fonts:
        return font_name
    else:
        return default_font

playing = []
num_playing = len(playing)

weapons_major= [
    "AR-23 解放者","AR-23C 解放者卡宾枪","StA-52 突击步枪","AR-23P 穿甲解放者","AR-23C 震荡解放者","BR-14 审判者","AR-61 肉锤","LAS-16 镰刀",
    "LAS-17 双刃镰刀","R-2124 宪法","R-63 勤勉","R-63CS 反狙击勤勉","SG-8S 重炮手","SMG-32 训斥","StA-11 SMG","SMG-37 防卫者","SMG-72 暴击斗士",
    "SG-20 止息","SG-8 制裁者","SG-451 野炊","SG-225 破裂者","SG-225SP 弥漫与祷告破裂者","SG-225IE 高燃破裂者","SG-22 丛林漫步者","JAR-5 主宰",
    "CB-9 爆燃弩","R-36 爆裂铳","ARC-12 雷霆","LAS-5 长柄镰","FLAM-66火炬手","SG-8P 等离子制裁者","PLAS-1 焦土","PLAS-101净化者"
]

weapons_sec = [
    "P-2 和平制造者", "P-19 救世主", "P-113 裁决者", "P-4 参议员", "GP-31 最后通牒", "GP-31 榴弹手枪",
    "P-72 打火机", "PLAS-15 忠诚", "LAS-7 匕首", "SG-22 游击兵", "P-11 治疗剂手枪", "CQC-19 眩晕长矛",
    "CQC-30 眩晕短棍", "CQC-5 战术斧"
]

weapons_throw = [
    "G-123 铝热弹", "G-12 高爆弹", "G-6 破片弹", "G-16 冲击弹", "G-50 追踪者", "G-10 燃烧弹", "G-13 燃烧冲击弹",
    "G-4 毒气弹", "G-3 烟雾弹", "G-23 震撼弹", "K-2 飞刀"
]

stm_RnG = [
    "轨道加特林火力网", "轨道空爆打击", "轨道120mm高爆弹火力网", "轨道380mm高爆弹火力网", "轨道游走火力网",
    "轨道激光炮", "轨道凝固汽油弹火力网",
    "轨道炮打击", "轨道精准打击", "飞鹰机枪扫射", "飞鹰空袭", "飞鹰集束炸弹", "飞鹰110mm火箭巢",
    "飞鹰凝固汽油弹", "飞鹰烟雾弹", "飞鹰500kg炸弹", "轨道毒气打击", "轨道烟雾弹打击", "轨道电磁冲击波打击",
    "重机枪部署支架", "反坦克炮部署支架", "能量护盾发生器", "特斯拉塔", "反步兵地雷", "反坦克地雷",
    "燃烧地雷", "毒气地雷", "哨戒机枪", "哨戒加特林", "自动哨戒炮", "哨戒火箭炮", "哨戒迫击炮",
    "哨戒电磁迫击炮"
]

stm_B = [
    "机枪", "重机枪", "盟友", "反器材步枪", "消耗性反坦克武器", "无后坐力步枪", "机炮", "火焰喷射器",
    "空爆火箭筒发射器", "突击兵", "磁轨炮", "飞矛", "W.A.S.P.发射器", "喷气背包", "快速侦察载具",
    "补给背包", "榴弹发射器", "激光大炮", "类星体加农炮", "护卫犬", "护卫犬“漫游车”", "护卫犬“腐息”",
    "防弹护盾背包", "能量护盾背包", "电弧发射器", "“爱国者”外骨骼装甲", "“解放者”外骨骼装甲", "定向护盾",
    "便携式地狱火背包"
]

arms = [
    "应对自如", "高效过滤", "电路导管", "工程包", "额外垫料", "强化", "易燃易爆", "集束炸药", "医疗包",
    "强健体格", "侦察", "伺服辅助", "蓄势出击", "毫不畏缩"
]

pacts_abs_E = [
    "星球轰炸：将任一战备替换为“轨道380mm高爆弹火力网”，且每当就绪时立即部署",
    "机械部件紧缺α：每个哨戒炮及地雷战备在一场任务至多部署5次",
    "油料处置：必须肃清遭遇的巡逻队", "剿灭：拆除哨站后必须肃清敌军", "蚊虫恐惧：禁止使用主武器攻击敌方空中单位",
    "玉碎：将任一战备替换为“便携式地狱火背包”", "八纮一宇：必须完成所有支线任务", "阴霾调查队：起始必须部署在超巨巢穴",
    "战争践踏：禁止使用高级武器攻击敌方强袭虫单位", "灭菌：必须拆除所有敌方哨站",
    "无形威胁：在完成主线任务前禁止拆除追踪虫巢穴", "改造抗拒：仅能配置不大于小队人数一半的Booster（向下取整）",
    "虫雾异变：将呼叫战略配备的按键颠倒（上-下，左-右）", "保持安全距离：禁止使用进攻型战略配备击杀穿刺虫",
    "酸蚀：禁止使用高级武器攻击吐酸泰坦", "定点供给：“重新补给”只能在主线任务区域及撤离区内呼叫",
    "用药管制：仅能在出现肢体异常（断臂、断腿、流血）时才允许使用治疗剂","预算紧缺：仅能在主线任务区域和撤离区主动呼叫增援（仅限多人）",
    "科研热忱：收集样本数需大于70%，且必须包含所有超级样本和变异虫卵",
    "火力管制：进攻型战略配备共享冷却时间（必须所有均就绪才允许部署其中一个）","一次性用品：禁止为高级武器拾取补给", "绝对绝境：选择一个战略配备，任务中禁止使用",
    "八该一反对：每次呼叫飞鹰后必须使用“飞鹰重新补给”","绝对资源管制：只有当任意武器消耗完全部弹药才允许拾取任意形式的子弹补给","孤立无援：每次任务增援预算减半",
    "弹药管理：仅在弹匣为空时允许换弹", "通讯中断：任务中禁止使用麦克风，并关闭游戏角色语音（仅多人）",
    "孢子采样：孢子喷涌虫和尖啸虫巢穴只能使用地狱火炸弹摧毁", "扼喉行动：必须清除超巨巢穴后才能执行主要任务（包括前置）",
    "清创战术：必须完成所有支线任务后才能执行主要任务（包括前置）",
    "斩首行动：必须优先消减视野可及的所有吐酸泰坦", "不自医：禁止对自己使用治疗剂"
]

pacts_abs_W = [
    "火海：将任一战备替换为“轨道凝固汽油弹火力网”，且每当就绪时立即部署", "八该一反对：每次呼叫飞鹰后必须使用“飞鹰重新补给”", "机械部件紧缺β：每个部署支架战备在一场任务至多部署5次",
    "嗜血：必须肃清遭遇的巡逻队", "剿灭：拆除哨站后必须肃清敌军", "绝对领空：禁止使用高级武器攻击敌方空中单位（包括炮艇、运输船）",
    "玉碎：将任一战备替换为“便携式地狱火背包”", "八纮一宇：必须完成所有支线任务", "市场花园行动：起始必须部署在堡垒",
    "战车风暴：禁止使用高级武器攻击敌方坦克单位", "死寂：必须拆除所有敌方哨站", "电磁对抗：将呼叫战略配备的按键颠倒（上-下，左-右）",
    "机枪压制：禁止使用高级武器攻击移动工厂", "定点供给：“重新补给”只能在主线任务区域及撤离区内呼叫", "用药管制：仅能在出现肢体异常（断臂、断腿、流血）时才允许使用治疗剂"
    "预算紧缺：仅能在主线任务区域和撤离区主动呼叫增援（仅限多人）", "绝对军备消减：禁止使用主武器", "轨道封锁：在主线任务完成前禁止使用轨道炮类战略配备",
    "全境封锁：在完成主线任务前禁止拆除战略配备干扰塔及炮艇设施（除任务需要）", "钢铁洪流：将任一战备替换为外骨骼装甲", "气体管制：禁止携带毒气、烟雾类投掷道具和战略配备",
    "弹药管理：仅在弹匣为空时允许换弹", "通讯中断：任务中禁止使用麦克风，并关闭游戏角色语音（仅多人）", "敌制空：若视野中存在炮艇单位，禁用来自飞鹰一号的空中支援",
    "绝对资源管制：只有当任意武器消耗完全部弹药才允许拾取任意形式的子弹补给","孤立无援：每次任务增援预算减半",
    "炮阵：禁止使用武器（包括主、副及高级武器）拆毁加农炮台单位", "扼喉行动：必须清除堡垒后才能执行主要任务（包括前置）",
    "清创战术：必须完成所有支线任务后才能执行主要任务（包括前置）","改造抗拒：仅能配置不大于小队人数一半的Booster（向下取整）",
    "斩首行动：必须优先消减视野可及的所有移动工厂", "不自医：禁止对自己使用治疗剂","科研热忱：收集样本数需大于70%，且必须包含所有超级样本和机密数据"
        ]

pacts_abs_S = [
    "星球轰炸：将任一战备替换为“轨道380mm高爆弹火力网”，且每当就绪时立即部署",
    "机械部件紧缺α：每个哨戒炮及地雷战备在一场任务至多部署5次",
    "民主铁拳：必须肃清遭遇的巡逻队", "剿灭：拆除哨站后必须肃清敌军", "应急响应程序：只能在推动任务或遭遇敌方增援时呼叫战略配备",
    "玉碎：将任一战备替换为“便携式地狱火背包”", "八纮一宇：必须完成所有支线任务", "废墟搜查：起始必须部署在城区中心",
    "科技封锁：禁止使用高级武器攻击敌方猎杀器单位", "真理过境：必须拆除所有敌方哨站",
    "思想控制：在完成主线任务前禁止拆除感知干扰器", "改造抗拒：仅能配置不大于小队人数一半的Booster（向下取整）",
    "心智侵蚀：将呼叫战略配备的按键颠倒（上-下，左-右）", "搜查令：必须使用武器破坏护盾后，使用武器拆毁穿梭舰",
    "定点供给：“重新补给”只能在主线任务区域及撤离区内呼叫",
    "用药管制：仅能在出现肢体异常（断臂、断腿、流血）时才允许使用治疗剂",
    "预算紧缺：仅能在主线任务区域和撤离区主动呼叫增援（仅限多人）",
    "科研热忱：收集样本数需大于70%，且必须包含所有超级样本",
    "火力管制：进攻型战略配备共享冷却时间（必须所有均就绪才允许部署其中一个）", "一次性用品：禁止为高级武器拾取补给",
    "绝对绝境：选择一个战略配备，任务中禁止使用",
    "八该一反对：每次呼叫飞鹰后必须使用“飞鹰重新补给”",
    "绝对资源管制：只有当任意武器消耗完全部弹药才允许拾取任意形式的子弹补给", "孤立无援：每次任务增援预算减半",
    "弹药管理：仅在弹匣为空时允许换弹", "通讯中断：任务中禁止使用麦克风，并关闭游戏角色语音（仅多人）",
    "孢子采样：孢子喷涌虫和尖啸虫巢穴只能使用地狱火炸弹摧毁",
    "清创战术：必须完成所有支线任务后才能执行主要任务（包括前置）",
    "斩首行动：必须优先消减视野可及的所有猎杀器", "不自医：禁止对自己使用治疗剂"
]

@register("miaomiao", "miaomiao", "喵喵开发的第一个插件", "1.2.1","https://github.com/miaoxutao123/astrbot_plugin_miaomiao")
class miaomiao(Star):
    def __init__(self, context: Context,config: dict):
        super().__init__(context)
        self.api_key = config.get("api_key")
        self.huggingface_api_url = config.get("huggingface_api_url")
        self.model = config.get("model")
        self.image_size = config.get("image_size")
        self.nap_server_address = config.get("nap_server_address")
        self.nap_server_port = config.get("nap_server_port")
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @command("为了超级地球")
    async def miaomiaomiao(self, event: AstrMessageEvent):
        '''民主问好'''
        user_name = event.get_sender_name()
        yield event.plain_result(f"民主向你问好, {user_name}!") # 发送一条纯文本消息

    @command("随机红战备")
    async def stratagem1(self, event: AstrMessageEvent):
        '''随机战备'''
        user_name = event.get_sender_name()
        foods = ["轨道加特林火力网", "轨道空爆打击", "轨道120mm高爆弹火力网", "轨道380mm高爆弹火力网", "轨道游走火力网", "轨道激光炮", "轨道凝固汽油弹火力网",
                 "轨道炮打击", "轨道精准打击", "飞鹰机枪扫射", "飞鹰空袭", "飞鹰集束炸弹", "飞鹰110mm火箭巢",
                 "飞鹰凝固汽油弹", "飞鹰烟雾弹", "飞鹰500kg炸弹", "轨道毒气打击", "轨道烟雾弹打击", "轨道电磁冲击波打击"
  
        ]
        choice = random.choice(foods)
        yield event.plain_result(f"潜兵【{user_name}】， 终端为你选择【{choice}】") # 发送一条纯文本消息

    @command("随机蓝战备")
    async def stratagem2(self, event: AstrMessageEvent):
        '''随机战备'''
        user_name = event.get_sender_name()
        foods = [
            "机枪", "重机枪", "盟友", "反器材步枪", "消耗性反坦克武器", "无后坐力步枪", "机炮", "火焰喷射器",
            "空爆火箭筒发射器", "突击兵", "磁轨炮", "飞矛", "W.A.S.P.发射器", "喷气背包", "快速侦察载具",
            "补给背包", "榴弹发射器", "激光大炮", "类星体加农炮", "护卫犬", "护卫犬“漫游车”", "护卫犬“腐息”",
            "防弹护盾背包", "能量护盾背包", "电弧发射器", "“爱国者”外骨骼装甲", "“解放者”外骨骼装甲", "定向护盾",
            "便携式地狱火背包"

        ]
        choice = random.choice(foods)
        yield event.plain_result(f"潜兵【{user_name}】， 终端为你选择【{choice}】")

    @command("随机绿战备")
    async def stratagem3(self, event: AstrMessageEvent):
        '''随机战备'''
        user_name = event.get_sender_name()
        foods = [
            "重机枪部署支架", "反坦克炮部署支架", "能量护盾发生器", "特斯拉塔", "反步兵地雷", "反坦克地雷",
            "燃烧地雷", "毒气地雷", "哨戒机枪", "哨戒加特林", "自动哨戒炮", "哨戒火箭炮", "哨戒迫击炮",
            "哨戒电磁迫击炮"

        ]
        choice = random.choice(foods)
        yield event.plain_result(f"潜兵【{user_name}】， 终端为你选择【{choice}】")



    @command("服役", alias = ["上机"])
    async def online(self, event: AstrMessageEvent):
        "登记服役"
        user_name = event.get_sender_name()
        if user_name in playing:
            yield event.plain_result(f"终端拒绝受理。理由：正在服役。")
        else :
            playing.append(user_name)
            num_playing = len(playing)
            yield event.plain_result(f"终端已受理潜兵【{user_name}】的服役申请，当前现役{num_playing}人")



    @command("退役", alias = ["下机"])
    async def offline(self, event: AstrMessageEvent):
        "登记退役"
        user_name = event.get_sender_name()
        if user_name not in playing:
            yield event.plain_result(f"终端拒绝受理。理由：非服役状态。")
            yield event.plain_result(f"⚠警告 拒绝服役涉违反《超级地球宪法》⚠")
            yield event.plain_result(f"最近的民主官正在向你靠近，请保持坐姿")
        else:
            playing.remove(user_name)
            num_playing = len(playing)
            yield event.plain_result(f"终端已受理潜兵【{user_name}】的退役申请，当前现役{num_playing}人")

    @command("查询服役")
    async  def check(self, event: AstrMessageEvent):
        "查询在役人数"
        num_playing = len(playing)
        players = ""
        for i in playing:
            players = players + i + "\n"

        yield event.plain_result(f"🟢当前现役{num_playing}人"
                                 f"\n🟢现役名单：\n{players}")

    @command("布拉什配装")
    async def ram_stm(self, event: AstrMessageEvent):
        "提供一套随机战备组合"
        user_name = event.get_sender_name()
        yield event.plain_result(f"终端已受理潜兵【{user_name}】的配装请求，请民主地等待……")
        stm = [
             "无后坐力步枪", "机炮", "空爆火箭筒发射器", "飞矛", "W.A.S.P.发射器",
             "“爱国者”外骨骼装甲", "“解放者”外骨骼装甲", "快速侦察载具",
            "喷气背包","补给背包", "护卫犬", "护卫犬“漫游车”", "护卫犬“腐息”",
            "防弹护盾背包", "能量护盾背包", "定向护盾", "便携式地狱火背包"

            "机枪", "重机枪", "盟友", "反器材步枪", "消耗性反坦克武器", "火焰喷射器","突击兵",
            "磁轨炮", "飞矛", "W.A.S.P.发射器","榴弹发射器", "激光大炮", "类星体加农炮",
            "电弧发射器", "“爱国者”外骨骼装甲", "“解放者”外骨骼装甲",

            "重机枪部署支架", "反坦克炮部署支架", "能量护盾发生器", "特斯拉塔", "反步兵地雷", "反坦克地雷",
            "燃烧地雷", "毒气地雷", "哨戒机枪", "哨戒加特林", "自动哨戒炮", "哨戒火箭炮", "哨戒迫击炮",
            "哨戒电磁迫击炮"

            "轨道加特林火力网", "轨道空爆打击", "轨道120mm高爆弹火力网", "轨道380mm高爆弹火力网", "轨道游走火力网",
            "轨道激光炮", "轨道凝固汽油弹火力网",
            "轨道炮打击", "轨道精准打击", "飞鹰机枪扫射", "飞鹰空袭", "飞鹰集束炸弹", "飞鹰110mm火箭巢",
            "飞鹰凝固汽油弹", "飞鹰烟雾弹", "飞鹰500kg炸弹", "轨道毒气打击", "轨道烟雾弹打击", "轨道电磁冲击波打击"
        ]
        stm1 = random.choice(stm)
        stm2 = random.choice(stm)
        i = 1
        while i == 1 :
            if stm1 == stm2:
                stm2 = random.choice(stm)
            else:
                i = 0
        time.sleep(1)
        yield event.plain_result(f"潜兵【{user_name}】，布拉什将军为你选择了【{stm1}】和【{stm2}】，请你民主地使用！")

    @command_group("绝对绝境")
    async def abs_(self):
        "真正的绝地潜兵不畏挑战！"

        pass
    @abs_.command("东线")
    async def absE(self, event: AstrMessageEvent, players: int = 1):
        try:
            if 1 <= players <= 4:
                user_name = event.get_sender_name()
                yield event.plain_result(f"终端已受理潜兵【{user_name}】发起的绝对绝境（东线）挑战请求，请民主地等待……")
                yield event.plain_result(f"⚠空前绝对的绝境代表绝对的绝地潜兵⚠\n请确保已使用积蓄购买战争基金后再执行任务！")


                msg = []
                msg.append(f"🔴已生成绝对配装:")
                for i in range(players):
                    maj = random.choice(weapons_major)
                    sec = random.choice(weapons_sec)
                    throw = random.choice(weapons_throw)
                    stm1 = random.choice(stm_B)
                    stm2, stm3, stm4 = random.sample(stm_RnG, 3)
                    arm = random.choice(arms)
                    msg.append(f"🔷整装{i+1}. 主武器【{maj}】，副武器【{sec}】，投掷物【{throw}】，战备【{stm1}】【{stm2}】【{stm3}】【{stm4}】，护甲词条【{arm}】")

                yield event.plain_result(f"{"\n".join(msg)}\n❗请依此分配各套整装！")

                pact1, pact2, pact3, pact4 = random.sample(pacts_abs_E, 4)
                yield event.plain_result(
                    f"🔴已生成本次行动的绝对战争条约：\n◽{pact1}\n◽{pact2}\n◽{pact3}\n◽{pact4}\n❗请注意：以上配装和条约在整个任务中均生效！在此基础上，小队需要完成主线任务并撤离。"
                )
            else:
                yield event.plain_result(f"终端拒绝受理。理由：错误的小队人数。")
        except:
            yield  event.plain_result(f"终端拒绝受理。理由：错误的小队人数。")

    @abs_.command("西线")
    async def absW(self, event: AstrMessageEvent, players: int = 1):
        try:
            if 1 <= players <=4:
                user_name = event.get_sender_name()
                yield event.plain_result(f"终端已受理潜兵【{user_name}】发起的绝对绝境（西线）挑战请求，请民主地等待……")
                yield event.plain_result(f"⚠空前绝对的绝境代表绝对的绝地潜兵⚠\n请确保已使用积蓄购买战争基金后再执行任务！")

                msg = []
                msg.append(f"🔴已生成绝对配装:")
                for i in range(players):
                    maj = random.choice(weapons_major)
                    sec = random.choice(weapons_sec)
                    throw = random.choice(weapons_throw)
                    stm1 = random.choice(stm_B)
                    stm2, stm3, stm4 = random.sample(stm_RnG, 3)
                    arm = random.choice(arms)
                    msg.append(
                        f"🔷整装{i + 1}. 主武器【{maj}】，副武器【{sec}】，投掷物【{throw}】，战备【{stm1}】【{stm2}】【{stm3}】【{stm4}】，护甲词条【{arm}】")

                yield event.plain_result(f"{"\n".join(msg)}\n❗请依此分配各套整装！")

                pact1, pact2, pact3, pact4 = random.sample(pacts_abs_W, 4)
                yield event.plain_result(
                    f"🔴已生成本次行动的绝对战争条约：\n◽{pact1}\n◽{pact2}\n◽{pact3}\n◽{pact4}\n❗请注意：以上配装和条约在整个任务中均生效！在此基础上，小队需要完成主线任务并撤离。"
                )
            else:
                yield event.plain_result(f"终端拒绝受理。理由：错误的小队人数。")

        except:
            yield  event.plain_result(f"终端拒绝受理。理由：错误的小队人数。")

    @abs_.command("南线")
    async def absS(self, event: AstrMessageEvent, players: int = 1):
        try:
            if 1 <= players <= 4:
                user_name = event.get_sender_name()
                yield event.plain_result(f"终端已受理潜兵【{user_name}】发起的绝对绝境（南线）挑战请求，请民主地等待……")
                yield event.plain_result(
                    f"⚠空前绝对的绝境代表绝对的绝地潜兵⚠\n请确保已使用积蓄购买战争基金后再执行任务！")

                msg = []
                msg.append(f"🔴已生成绝对配装:")
                for i in range(players):
                    maj = random.choice(weapons_major)
                    sec = random.choice(weapons_sec)
                    throw = random.choice(weapons_throw)
                    stm1 = random.choice(stm_B)
                    stm2, stm3, stm4 = random.sample(stm_RnG, 3)
                    arm = random.choice(arms)
                    msg.append(
                        f"🔷整装{i + 1}. 主武器【{maj}】，副武器【{sec}】，投掷物【{throw}】，战备【{stm1}】【{stm2}】【{stm3}】【{stm4}】，护甲词条【{arm}】")

                yield event.plain_result(f"{"\n".join(msg)}\n❗请依此分配各套整装！")

                pact1, pact2, pact3, pact4 = random.sample(pacts_abs_S, 4)
                yield event.plain_result(
                    f"🔴已生成本次行动的绝对战争条约：\n◽{pact1}\n◽{pact2}\n◽{pact3}\n◽{pact4}\n❗请注意：以上配装和条约在整个任务中均生效！在此基础上，小队需要完成主线任务并撤离。"
                )
            else:
                yield event.plain_result(f"终端拒绝受理。理由：错误的小队人数。")
        except:
            yield event.plain_result(f"终端拒绝受理。理由：错误的小队人数。")



    @command("绝地试炼西线")
    async def divetrainW(self, event: AstrMessageEvent):
        "提供一套挑战因子增加游戏难度"
        user_name = event.get_sender_name()
        yield event.plain_result(f"终端已受理潜兵【{user_name}】的绝地试炼（西线）请求，请民主地等待……")
        yield event.plain_result(f"⚠请注意：即将生成的战争条约可能会大幅增加游戏难度⚠\n请确保已使用积蓄购买战争基金后再执行任务！")
        pacts = [
        "衣不蔽体：必须选择轻甲", "火海：必须携带“轨道凝固汽油弹火力网”，且每当就绪时立即部署", "低气压：飞鹰一号无法在战区提供支援", "马达故障：禁止选用哨戒炮及部署支架战备",
        "嗜血：必须肃清遭遇的巡逻队", "剿灭：拆除哨站后必须肃清敌军", "丢失制空：禁止使用高级武器攻击敌方空中单位",
        "玉碎：必须携带“便携式地狱火背包”", "八纮一宇：必须完成所有支线任务", "市场花园行动：起始必须部署在堡垒",
        "战车风暴：禁止使用高级武器攻击敌方坦克单位", "死寂：必须拆除所有敌方哨站", "电磁对抗：将呼叫战略配备的按键颠倒（上-下，左-右）",
        "震慑：禁止使用高级武器攻击移动工厂", "定点供给：“重新补给”只能在主线任务区域及撤离区内呼叫", "药物依赖：在生命值不满的状态时，必须使用治疗剂"
        "预算紧缺：仅能在主线任务区域和撤离区主动呼叫增援（仅限多人）", "军备消减：禁止使用主武器", "轨道封锁：在主线任务完成前禁止使用轨道炮类战略配备",
        "全境封锁：在完成主线任务前禁止拆除战略配备干扰塔及炮艇设施（除任务需要）", "钢铁洪流：必须携带外骨骼装甲", "气体管制：禁止携带毒气、烟雾类投掷道具和战略配备"
        ]
        pact1 = random.choice(pacts)
        pacts.remove(pact1)
        pact2 = random.choice(pacts)
        pacts.remove(pact2)
        pact3 = random.choice(pacts)
        time.sleep(1)
        yield event.plain_result(f"潜兵【{user_name}】，绝地试炼任务已生成。\n本次任务生效的战争条约为：\n🔴{pact1}\n🔴{pact2}\n🔴{pact3}\n❗在此基础上，小队必须完成主线任务并成功撤离。")

    @command("绝地试炼东线")
    async def divetrainE(self, event: AstrMessageEvent):
        "提供一套挑战因子增加游戏难度"
        user_name = event.get_sender_name()
        yield event.plain_result(f"终端已受理潜兵【{user_name}】的绝地试炼（东线）请求，请民主地等待……")
        yield event.plain_result(f"⚠请注意：即将生成的战争条约可能会大幅增加游戏难度⚠\n请确保已使用积蓄购买战争基金后再执行任务！")
        pacts = [
            "寸步难行：必须选择重甲", "星球轰炸：必须携带“轨道380mm高爆弹火力网”，且每当就绪时立即部署",
            "大气波动：不能携带超过一个的轨道炮战略配备", "机械故障：禁止选用哨戒炮及地雷战备",
            "油料处置：必须肃清遭遇的巡逻队", "剿灭：拆除哨站后必须肃清敌军", "蚊虫恐惧：禁止使用主武器攻击敌方空中单位",
            "玉碎：必须携带“便携式地狱火背包”", "八纮一宇：必须完成所有支线任务", "市场花园行动：起始必须部署在超巨巢穴",
            "战争践踏：禁止使用高级武器攻击敌方强袭虫单位", "灭菌：必须拆除所有敌方哨站", "无形威胁：在完成主线任务前禁止拆除追踪虫巢穴",
            "虫雾异变：将呼叫战略配备的按键颠倒（上-下，左-右）", "斩首：禁止使用进攻型战略配备击杀穿刺虫",
            "酸蚀：禁止使用高级武器攻击吐酸泰坦", "定点供给：“重新补给”只能在主线任务区域及撤离区内呼叫", "工业革命：必须携带快速侦察载具",
            "药物依赖：在生命值不满的状态时，必须使用治疗剂", "严禁烟火：禁止携带爆炸类和燃烧类的主、副武器及投掷道具",
            "预算紧缺：仅能在主线任务区域和撤离区主动呼叫增援（仅限多人）", "军备消减：禁止使用无后座力步枪及类星体加农炮", "科研热忱：收集样本数需大于70%，且必须包含所有超级样本和变异虫卵"
        ]
        pact1 = random.choice(pacts)
        pacts.remove(pact1)
        pact2 = random.choice(pacts)
        pacts.remove(pact2)
        pact3 = random.choice(pacts)
        time.sleep(1)
        yield event.plain_result(
            f"潜兵【{user_name}】，绝地试炼任务已生成。\n本次任务生效的战争条约为：\n🔴{pact1}\n🔴{pact2}\n🔴{pact3}\n❗在此基础上，小队必须完成主线任务并成功撤离。")

    @command("绝地试炼南线")
    async def divetrainS(self, event: AstrMessageEvent):
        "提供一套挑战因子增加游戏难度"
        user_name = event.get_sender_name()
        yield event.plain_result(f"终端已受理潜兵【{user_name}】的绝地试炼（南线）请求，请民主地等待……")
        yield event.plain_result(f"⚠请注意：即将生成的战争条约可能会大幅增加游戏难度⚠\n请确保已使用积蓄购买战争基金后再执行任务！")
        pacts = [
            "防弹衣：必须选择“额外垫料”护甲", "轨道定位失效：轨道炮战略配备无法在战区提供支援",
            "航空管制：不能携带超过一个飞鹰战略配备", "机械故障：禁止选用哨戒炮及地雷战备",
            "民主铁拳：必须肃清遭遇的巡逻队", "应急响应程序：只能在推动任务或遭遇敌方增援时呼叫战略配备",
            "玉碎：必须携带“便携式地狱火背包”", "八纮一宇：必须完成所有支线任务", "市场花园行动：起始必须部署在地图正中",
            "资源污染：禁止获取城区内的补给资源", "真理过境：必须拆除所有敌方哨站", "思想控制：在完成主线任务前禁止拆除感知干扰器",
            "心智侵蚀：将呼叫战略配备的按键颠倒（上-下，左-右）", "科技封锁：禁止使用高级武器击杀猎杀器",
            "低空避障失灵：禁止使用护卫犬系列战略配备", "定点供给：“重新补给”只能在主线任务区域及撤离区内呼叫", "原始崇拜：必须携带冷兵器，禁止使用载具",
            "药物依赖：在生命值不满的状态时，必须使用治疗剂", "气体管制：禁止携带毒气、烟雾类投掷道具和战略配备",
            "预算紧缺：仅能在主线任务区域和撤离区主动呼叫增援（仅限多人）", "军备消减：禁止使用无后座力步枪及类星体加农炮",
            "科研热忱：收集样本数需大于70%，且必须包含所有超级样本"
        ]
        pact1 = random.choice(pacts)
        pacts.remove(pact1)
        pact2 = random.choice(pacts)
        pacts.remove(pact2)
        pact3 = random.choice(pacts)
        time.sleep(1)
        yield event.plain_result(
            f"潜兵【{user_name}】，绝地试炼任务已生成。\n本次任务生效的战争条约为：\n🔴{pact1}\n🔴{pact2}\n🔴{pact3}\n❗在此基础上，小队必须完成主线任务并成功撤离。")

    @command("v50", alias = ["V50"])
    async def v50(self, event: AstrMessageEvent):
        """v我50！"""
        yield event.plain_result(
            Image.open("v50.png")
        )
            
    @command("喜报")
    async def congrats(self, message: AstrMessageEvent):
        '''喜报生成器'''
        msg = message.message_str.replace("喜报", "").strip()
        for i in range(20, len(msg), 20):
            msg = msg[:i] + "\n" + msg[i:]

        path = os.path.abspath(os.path.dirname(__file__))
        bg = path + "/congrats.jpg"
        img = PILImage.open(bg)
        draw = PILImageDraw.Draw(img)
        font = PILImageFont.truetype(path + "/simhei.ttf", 65)

        # Calculate the width and height of the text
        text_width, text_height = draw.textbbox((0, 0), msg, font=font)[2:4]

        # Calculate the starting position of the text to center it.
        x = (img.size[0] - text_width) / 2
        y = (img.size[1] - text_height) / 2

        draw.text(
            (x, y),
            msg,
            font=font,
            fill=(255, 0, 0),
            stroke_width=3,
            stroke_fill=(255, 255, 0),
        )

        img.save("congrats_result.jpg")
        return CommandResult().file_image("congrats_result.jpg")