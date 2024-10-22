import uuid
import models

if __name__ == "__main__":
    models.db.connect()
    lv1 = [
        [210000, '采掘'],
        [220000, '化工'],
        [230000, '钢铁'],
        [240000, '有色金属'],
        [610000, '建筑材料/建筑建材'],
        [620000, '建筑装饰'],
        [630000, '电气设备'],
        [640000, '机械设备'],
        [650000, '国防军工'],
        [280000, '汽车/交运设备'],
        [330000, '家用电器'],
        [360000, '轻工制造'],
        [110000, '农林牧渔'],
        [340000, '食品饮料'],
        [350000, '纺织服装'],
        [370000, '医药生物'],
        [450000, '商业贸易'],
        [460000, '休闲服务'],
        [270000, '电子'],
        [710000, '计算机'],
        [720000, '传媒/信息服务'],
        [730000, '通信'],
        [410000, '公用事业'],
        [420000, '交通运输'],
        [430000, '房地产'],
        [480000, '银行'],
        [490000, '非银金融'],
        [510000, '综合'],
    ]

    lv2 = [
        [210100, '石油开采'],
        [210200, '煤炭开采'],
        [210300, '其他采掘'],
        [210400, '采掘服务'],
        [220100, '石油化工'],
        [220200, '化学原料'],
        [220300, '化学制品'],
        [220400, '化学纤维'],
        [220500, '塑料'],
        [220600, '橡胶'],
        [230100, '钢铁'],
        [240300, '工业金属'],
        [240400, '黄金'],
        [240500, '稀有金属'],
        [240200, '金属非金属新材料'],
        [610100, '水泥制造'],
        [610200, '玻璃制造'],
        [610300, '其他建材'],
        [620100, '房屋建设'],
        [620200, '装修装饰'],
        [620300, '基础建设'],
        [620400, '专业工程'],
        [620500, '园林工程'],
        [630100, '电机'],
        [630200, '电气自动化设备'],
        [630300, '电源设备'],
        [630400, '高低压设备'],
        [640100, '通用机械'],
        [640200, '专用设备'],
        [640300, '仪器仪表'],
        [640400, '金属制品'],
        [640500, '运输设备'],
        [650100, '航天装备'],
        [650200, '航空装备'],
        [650300, '地面兵装'],
        [650400, '船舶制造'],
        [280100, '汽车整车'],
        [280200, '汽车零部件'],
        [280300, '汽车服务'],
        [280400, '其他交运设备'],
        [330100, '白色家电'],
        [330200, '视听器材'],
        [360100, '造纸'],
        [360200, '包装印刷'],
        [360300, '家用轻工'],
        [360400, '其他轻工制造'],
        [110100, '种植业'],
        [110200, '渔业'],
        [110300, '林业'],
        [110400, '饲料'],
        [110500, '农产品加工'],
        [110600, '农业综合'],
        [110700, '畜禽养殖'],
        [110800, '动物保健'],
        [340300, '饮料制造'],
        [340400, '食品加工'],
        [350100, '纺织制造'],
        [350200, '服装家纺'],
        [370100, '化学制药'],
        [370200, '中药'],
        [370300, '生物制品'],
        [370400, '医药商业'],
        [370500, '医疗器械'],
        [370600, '医疗服务'],
        [450300, '一般零售'],
        [450400, '专业零售'],
        [450500, '商业物业经营'],
        [450200, '贸易'],
        [460100, '景点'],
        [460200, '酒店'],
        [460300, '旅游综合'],
        [460400, '餐饮'],
        [460500, '其他休闲服务'],
        [270100, '半导体'],
        [270200, '元件'],
        [270300, '光学光电子'],
        [270500, '电子制造'],
        [270400, '其他电子'],
        [710100, '计算机设备'],
        [710200, '计算机应用'],
        [720100, '文化传媒'],
        [720200, '营销传播'],
        [720300, '互联网传媒'],
        [730100, '通信运营'],
        [730200, '通信设备'],
        [410100, '电力'],
        [410200, '水务'],
        [410300, '燃气'],
        [410400, '环保工程及服务'],
        [420100, '港口'],
        [420200, '高速公路'],
        [420300, '公交'],
        [420400, '航空运输'],
        [420500, '机场'],
        [420600, '航运'],
        [420700, '铁路运输'],
        [420800, '物流'],
        [430100, '房地产开发'],
        [430200, '园区开发'],
        [480100, '银行'],
        [490100, '证券'],
        [490200, '保险'],
        [490300, '多元金融'],
        [510100, '综合'],
    ]

    lv3 = [
        [210101, '石油开采'],
        [210201, '煤炭开采'],
        [210202, '焦炭加工'],
        [210301, '其他采掘'],
        [210401, '油气钻采服务'],
        [210402, '其他采掘服务'],
        [220101, '石油加工'],
        [220103, '石油贸易'],
        [220201, '纯碱'],
        [220202, '氯碱'],
        [220203, '无机盐'],
        [220204, '其他化学原料'],
        [220301, '氮肥'],
        [220302, '磷肥'],
        [220303, '农药'],
        [220304, '日用化学产品'],
        [220305, '涂料油漆油墨制造'],
        [220306, '钾肥'],
        [220310, '复合肥'],
        [220307, '民爆用品'],
        [220308, '纺织化学用品'],
        [220311, '氟化工及制冷剂'],
        [220312, '磷化工及磷酸盐'],
        [220313, '聚氨酯'],
        [220314, '玻纤'],
        [220309, '其他化学制品'],
        [220401, '涤纶'],
        [220402, '维纶'],
        [220403, '粘胶'],
        [220404, '其他纤维'],
        [220405, '氨纶'],
        [220501, '其他塑料制品'],
        [220502, '合成革'],
        [220503, '改性塑料'],
        [220601, '轮胎'],
        [220603, '炭黑'],
        [220602, '其他橡胶制品'],
        [230101, '普钢'],
        [230102, '特钢'],
        [240301, '铝'],
        [240302, '铜'],
        [240303, '铅锌'],
        [240401, '黄金'],
        [240501, '稀土'],
        [240502, '钨'],
        [240503, '锂'],
        [240504, '其他稀有小金属'],
        [240201, '金属新材料'],
        [240202, '磁性材料'],
        [240203, '非金属新材料'],
        [610101, '水泥制造'],
        [610201, '玻璃制造'],
        [610301, '耐火材料'],
        [610302, '管材'],
        [610303, '其他建材'],
        [620101, '房屋建设'],
        [620201, '装修装饰'],
        [620301, '城轨建设'],
        [620302, '路桥施工'],
        [620303, '水利工程'],
        [620304, '铁路建设'],
        [620305, '其他基础建设'],
        [620401, '钢结构'],
        [620402, '化学工程'],
        [620403, '国际工程承包'],
        [620404, '其他专业工程'],
        [620501, '园林工程'],
        [630101, '电机'],
        [630201, '电网自动化'],
        [630202, '工控自动化'],
        [630203, '计量仪表'],
        [630301, '综合电力设备商'],
        [630302, '风电设备'],
        [630303, '光伏设备'],
        [630304, '火电设备'],
        [630305, '储能设备'],
        [630306, '其它电源设备'],
        [630401, '高压设备'],
        [630402, '中压设备'],
        [630403, '低压设备'],
        [630404, '线缆部件及其他'],
        [640101, '机床工具'],
        [640102, '机械基础件'],
        [640103, '磨具磨料'],
        [640104, '内燃机'],
        [640105, '制冷空调设备'],
        [640106, '其它通用机械'],
        [640201, '工程机械'],
        [640202, '重型机械'],
        [640203, '冶金矿采化工设备'],
        [640204, '楼宇设备'],
        [640205, '环保设备'],
        [640206, '纺织服装设备'],
        [640207, '农用机械'],
        [640208, '印刷包装机械'],
        [640209, '其它专用机械'],
        [640301, '仪器仪表'],
        [640401, '金属制品'],
        [640501, '铁路设备'],
        [650101, '航天装备'],
        [650201, '航空装备'],
        [650301, '地面兵装'],
        [650401, '船舶制造'],
        [280101, '乘用车'],
        [280102, '商用载货车'],
        [280103, '商用载客车'],
        [280201, '汽车零部件'],
        [280301, '汽车服务'],
        [280401, '其他交运设备'],
        [330101, '冰箱'],
        [330102, '空调'],
        [330103, '洗衣机'],
        [330104, '小家电'],
        [330105, '家电零部件'],
        [330201, '彩电'],
        [330202, '其它视听器材'],
        [360101, '造纸'],
        [360201, '包装印刷'],
        [360302, '家具'],
        [360303, '其他家用轻工'],
        [360304, '珠宝首饰'],
        [360305, '文娱用品'],
        [360401, '其他轻工制造'],
        [110101, '种子生产'],
        [110102, '粮食种植'],
        [110103, '其他种植业'],
        [110201, '海洋捕捞'],
        [110202, '水产养殖'],
        [110301, '林业'],
        [110401, '饲料'],
        [110501, '果蔬加工'],
        [110502, '粮油加工'],
        [110504, '其他农产品加工'],
        [110601, '农业综合'],
        [110701, '畜禽养殖'],
        [110801, '动物保健'],
        [340301, '白酒'],
        [340302, '啤酒'],
        [340303, '其他酒类'],
        [340304, '软饮料'],
        [340305, '葡萄酒'],
        [340306, '黄酒'],
        [340401, '肉制品'],
        [340402, '调味发酵品'],
        [340403, '乳品'],
        [340404, '食品综合'],
        [350101, '毛纺'],
        [350102, '棉纺'],
        [350103, '丝绸'],
        [350104, '印染'],
        [350104, '印染'],
        [350105, '辅料'],
        [350106, '其他纺织'],
        [350202, '男装'],
        [350203, '女装'],
        [350204, '休闲服装'],
        [350205, '鞋帽'],
        [350206, '家纺'],
        [350207, '其他服装'],
        [370101, '化学原料药'],
        [370102, '化学制剂'],
        [370201, '中药'],
        [370301, '生物制品'],
        [370401, '医药商业'],
        [370501, '医疗器械'],
        [370601, '医疗服务'],
        [450301, '百货'],
        [450302, '超市'],
        [450303, '多业态零售'],
        [450401, '专业连锁'],
        [450501, '一般物业经营'],
        [450502, '专业市场'],
        [450201, '贸易'],
        [460101, '人工景点'],
        [460102, '自然景点'],
        [460201, '酒店'],
        [460301, '旅游综合'],
        [460401, '餐饮'],
        [460501, '其他休闲服务'],
        [270101, '集成电路'],
        [270102, '分立器件'],
        [270103, '半导体材料'],
        [270202, '印制电路板'],
        [270203, '被动元件'],
        [270301, '显示器件'],
        [270302, 'LED'],
        [270303, '光学元件'],
        [270501, '电子系统组装'],
        [270502, '电子零部件制造'],
        [270401, '其他电子'],
        [710101, '计算机设备'],
        [710201, '软件开发'],
        [710202, 'IT服务'],
        [720101, '平面媒体'],
        [720102, '影视动漫'],
        [720103, '有线电视网络'],
        [720104, '其他文化传媒'],
        [720201, '营销服务'],
        [720301, '互联网信息服务'],
        [720302, '移动互联网服务'],
        [720303, '其他互联网服务'],
        [730101, '通信运营'],
        [730201, '终端设备'],
        [730202, '通信传输设备'],
        [730203, '通信配套服务'],
        [410101, '火电'],
        [410102, '水电'],
        [410103, '燃机发电'],
        [410104, '热电'],
        [410105, '新能源发电'],
        [410201, '水务'],
        [410301, '燃气'],
        [410401, '环保工程及服务'],
        [420101, '港口'],
        [420201, '高速公路'],
        [420301, '公交'],
        [420401, '航空运输'],
        [420501, '机场'],
        [420601, '航运'],
        [420701, '铁路运输'],
        [420801, '物流'],
        [430101, '房地产开发'],
        [430201, '园区开发'],
        [480101, '银行'],
        [490101, '证券'],
        [490201, '保险'],
        [490301, '多元金融'],
        [510101, '综合'],
    ]

    # models.db.connect()
    models.db.create_tables([models.ShenWanIndustry])

    for each_lv1 in lv1:
        models.ShenWanIndustry.create(
            uuid=uuid.uuid4(),
            industry_name = each_lv1[1],
            industry_code = each_lv1[0],
            level = 1,
        )
    
    for each_lv2 in lv2:
        models.ShenWanIndustry.create(
            uuid=uuid.uuid4(),
            industry_name = each_lv2[1],
            industry_code = each_lv2[0],
            level = 2,
        )

    for each_lv3 in lv3:
        models.ShenWanIndustry.create(
            uuid=uuid.uuid4(),
            industry_name = each_lv3[1],
            industry_code = each_lv3[0],
            level = 3,
        )
