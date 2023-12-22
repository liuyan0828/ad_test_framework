"""
-*- coding: utf-8 -*-
@Time : 2021/12/7
@Author : liuyan
@function : 对比两个xml文件的异同
2022.5.27 更新 增加JSON处理
"""

import xml.etree.ElementTree as ET
import json
from utils.UrlHandler import UrlHandler


class CompareXml(object):

    @staticmethod
    def get_root(filepath):
        tree = ET.parse(filepath)
        return tree.getroot()

    @staticmethod
    def get_all_elements(root, status):
        """
        处理值，去除其中的\t\n字符，如果是http开头的字符串，去除指定host中的指定字段，如果是None，设置为空字符串
        :return: 返回xml文件中所有的子节点,格式为[tag名, 属性， 值]
        """
        ele_list = {}
        for i in root.iter():
            if i.tag != ("ExpireTime" or "RemainClick"):
                if i.tag != "SupportUnion":
                    if i.text is None:
                        i.text = ''
                    i.text = i.text.strip()
                    if i.tag in ['Impression', 'CompanionClickTracking']:
                        if 'id' in i.attrib.keys():
                            if i.attrib['id'] in ['mma', 'miaozhen', 'admaster', 'other']:
                                h_url = UrlHandler(i.text)
                                i.text = h_url.get_host()
                                print(i.tag, i.attrib, i.text)
                    if i.text.startswith('http'):
                        handle_url = UrlHandler(i.text)
                        i.text = handle_url.delete_specified_params(['mmgtest.aty.sohu.com', 'mmg.aty.sohu.com'],
                                                                    ["vu", 'du', 'appid', 'encd', "cheattype", 'rt',
                                                                     'platsource', 'sign', 'warmup', 'rip', 'fip',
                                                                     'v2code', 'bt', 'backtest', 'bk', 'sperotime',
                                                                     "impressionid", "flightid", "sspreqid", "sip",
                                                                     "indexip", "v2","encrysig","dx","dy","ux","uy","pgcauthor","vc"])
                        i.text = handle_url.delete_specified_params(['data.vod.itc.cn'],
                                                                    ["sig","prod","new"])
                        if status == 10001:
                            i.text = handle_url.delete_specified_params(['mmgtest.aty.sohu.com', 'mmg.aty.sohu.com'],
                                                                        ["tvid", "crid", "ar", "datatype"])
                    if i.tag in ele_list.keys():
                        ele_list[i.tag].append({'att': i.attrib, 'text': i.text})
                    else:
                        ele_list[i.tag] = [{'att': i.attrib, 'text': i.text}]
        return ele_list


class JsonHandle:

    # 只支持字典、列表嵌套的数据格式
    @staticmethod
    def get_target_result(dic):
        """
        :param dic: 需要处理的数据
        :return: 处理后的dic
        """
        if not dic:
            return 'argv[1] cannot be empty'
        # 对传入数据进行格式校验
        if not isinstance(dic, dict) and not isinstance(dic, list):
            return 'argv[1] not an dict or an list '
        if isinstance(dic, dict):
            for k, v in dic.items():
                if isinstance(v, str) and v.startswith('http'):
                    handle_url = UrlHandler(v)
                    v = handle_url.delete_specified_params(['mmgtest.aty.sohu.com', 'mmg.aty.sohu.com'],
                                                                ["vu", 'du', 'appid', 'encd', "cheattype", 'rt',
                                                                 'platsource', 'sign', 'warmup', 'rip', 'fip', 'v2code',
                                                                 'bt', 'backtest', 'bk', 'sperotime', "impressionid",
                                                                 "flightid", "sspreqid","v1code","vc","sip"])
                    # 将URL处理成字典形式存入
                    dic[k] = {}
                    dic[k]['path'] = v.split('?')[0]
                    dic[k].update(handle_url.get_all_params())
                # if isinstance(v, list):
                else:
                    JsonHandle.get_target_result(dic[k])
        else:
            # 如果数据类型为列表，遍历列表调用get_target_result函数
            for j in dic:
                JsonHandle.get_target_result(j)
        return dic


res ={
            "ads": [
                {
                    "pt": "open",
                    "ad": [
                        {
                            "adgroup": {
                                "lineid": "417762",
                                "advid": "11635",
                                "saletype": 1,
                                "campaignid": "12621",
                                "tradetype": 0,
                                "posnum": 2
                            },
                            "adtype": 0,
                            "adfrom": "ade",
                            "event_monitor": [
                                {
                                    "url": "http://mmg.aty.sohu.com/pv?type=1&du=0&rt=1700032799115_6559_10.33.8.134_15_15&spead=0&plat=3&sver=9.9.20&poid=1&adplat=2&prot=json&protv=3.0&build=com.sohu.inhouse.iphonevideo&appid=tv&adoriginal=sohu&sdkVersion=15.9.1&offline=0&density=2.000000&displayMetrics=375*667&islocaltv=0&bt=20231115&endtime=20231231&ad=54962&b=417762&bk=117199509&pagetype=2&islocaltv=0&seq=1&w=1080&h=1920&wdbn=1080&hgbn=1920&cheattype=0&sperotime=1700032799&site=1&template=video&platsource=tv&indexip=adveng-retrvl-qa.ns-adveng-qa.svc.cluster.local:60111&backtest=ctr_cheat,pacing_ad_alloc_a,exp_nobidfloor,pdb_load_a,pdb_opt_a&ispgc=0&impressionid=7528c6f1f2089fe9a5e9dc4a70456d2d&scope=0&flightid=36609765&from=tvssp&advertiserid=11635&encd=92I3jLba%2FU8Tivxo0cfnxsGaxS0pwzAx9oO%2FNuFkHj6UXrQcMXwZW%2F0NPfH2QwiybpqwJqyftA1LozHeFj61jqs3U07L6anVRF%2FRZlASkCbNExR6QnM0%2FhhbC6TXvdkQKcwTUx05wkGgkhcFBO4yJio6hpIRGtcKXue2Wp76oByPpYD%2F2u1cdme7H%2FZExrh5IWzwb1ruZFkNChV%2FEs7QlZ0vrzJ8c260E6ngocShU1hjNZCMri4e8lWczTGrGTElL20lPoIfsUG6D8JNeBZ%2BZm%2Bqww%2Bsyd1D50tHcbOw5GOHOpFk1IhAna8%2FRm8cCbJMiCiUTpDYLZuE0c96iGqBYnqU%2BtSgIugMekH2yrTpx9iPpAYtbRVK7C8JPrX1sYPAexQRUikYg%2F0ddLYFyMPw2C1WR9fKvY6VpnfXOzerIgfSv%2BiKEzVUvn2igUimxsyVmb0ZVAKQBgAenHsrZP6JO6U20yI%3D&vp=s&at=0&c=2741&p=op&posid=op_iphone_1&loc=Unknown&adstyle=open&ac=5487&ad=54962&pt=12621&b=417762&bk=117199509&pagetype=2&spead=0&rtm=__TIME__&err=[ERRORCODE]",
                                    "event": 0,
                                    "tag": "sohu"
                                },
                                {
                                    "url": "http://mmg.aty.sohu.com/av?du=0&rt=1700032799115_6559_10.33.8.134_15_15&spead=0&plat=3&sver=9.9.20&poid=1&adplat=2&prot=json&protv=3.0&build=com.sohu.inhouse.iphonevideo&appid=tv&adoriginal=sohu&sdkVersion=15.9.1&offline=0&density=2.000000&displayMetrics=375*667&islocaltv=0&bt=20231115&endtime=20231231&ad=54962&b=417762&bk=117199509&pagetype=2&islocaltv=0&seq=1&w=1080&h=1920&wdbn=1080&hgbn=1920&cheattype=0&sperotime=1700032799&site=1&template=video&platsource=tv&indexip=adveng-retrvl-qa.ns-adveng-qa.svc.cluster.local:60111&backtest=ctr_cheat,pacing_ad_alloc_a,exp_nobidfloor,pdb_load_a,pdb_opt_a&ispgc=0&impressionid=7528c6f1f2089fe9a5e9dc4a70456d2d&scope=0&flightid=36609765&from=tvssp&advertiserid=11635&encd=92I3jLba%2FU8Tivxo0cfnxsGaxS0pwzAx9oO%2FNuFkHj6UXrQcMXwZW%2F0NPfH2QwiybpqwJqyftA1LozHeFj61jqs3U07L6anVRF%2FRZlASkCbNExR6QnM0%2FhhbC6TXvdkQKcwTUx05wkGgkhcFBO4yJio6hpIRGtcKXue2Wp76oByPpYD%2F2u1cdme7H%2FZExrh5IWzwb1ruZFkNChV%2FEs7QlZ0vrzJ8c260E6ngocShU1hjNZCMri4e8lWczTGrGTElL20lPoIfsUG6D8JNeBZ%2BZm%2Bqww%2Bsyd1D50tHcbOw5GOHOpFk1IhAna8%2FRm8cCbJMiCiUTpDYLZuE0c96iGqBYnqU%2BtSgIugMekH2yrTpx9iPpAYtbRVK7C8JPrX1sYPAexQRUikYg%2F0ddLYFyMPw2C1WR9fKvY6VpnfXOzerIgfSv%2BiKEzVUvn2igUimxsyVmb0ZVAKQBgAenHsrZP6JO6U20yI%3D&vp=s&at=0&c=2741&p=op&posid=op_iphone_1&loc=Unknown&adstyle=open&ac=5487&ad=54962&pt=12621&b=417762&bk=117199509&pagetype=2&rtm=__TIME__",
                                    "event": 1,
                                    "tag": "sohu"
                                },
                                {
                                    "url": "http://mmg.aty.sohu.com/pvlog?du=0&rt=1700032799115_6559_10.33.8.134_15_15&spead=0&plat=3&sver=9.9.20&poid=1&adplat=2&prot=json&protv=3.0&build=com.sohu.inhouse.iphonevideo&appid=tv&adoriginal=sohu&sdkVersion=15.9.1&offline=0&density=2.000000&displayMetrics=375*667&islocaltv=0&bt=20231115&endtime=20231231&ad=54962&b=417762&bk=117199509&pagetype=2&islocaltv=0&seq=1&w=1080&h=1920&wdbn=1080&hgbn=1920&cheattype=0&sperotime=1700032799&site=1&template=video&platsource=tv&indexip=adveng-retrvl-qa.ns-adveng-qa.svc.cluster.local:60111&backtest=ctr_cheat,pacing_ad_alloc_a,exp_nobidfloor,pdb_load_a,pdb_opt_a&ispgc=0&impressionid=7528c6f1f2089fe9a5e9dc4a70456d2d&scope=0&flightid=36609765&from=tvssp&advertiserid=11635&encd=92I3jLba%2FU8Tivxo0cfnxsGaxS0pwzAx9oO%2FNuFkHj6UXrQcMXwZW%2F0NPfH2QwiybpqwJqyftA1LozHeFj61jqs3U07L6anVRF%2FRZlASkCbNExR6QnM0%2FhhbC6TXvdkQKcwTUx05wkGgkhcFBO4yJio6hpIRGtcKXue2Wp76oByPpYD%2F2u1cdme7H%2FZExrh5IWzwb1ruZFkNChV%2FEs7QlZ0vrzJ8c260E6ngocShU1hjNZCMri4e8lWczTGrGTElL20lPoIfsUG6D8JNeBZ%2BZm%2Bqww%2Bsyd1D50tHcbOw5GOHOpFk1IhAna8%2FRm8cCbJMiCiUTpDYLZuE0c96iGqBYnqU%2BtSgIugMekH2yrTpx9iPpAYtbRVK7C8JPrX1sYPAexQRUikYg%2F0ddLYFyMPw2C1WR9fKvY6VpnfXOzerIgfSv%2BiKEzVUvn2igUimxsyVmb0ZVAKQBgAenHsrZP6JO6U20yI%3D&vp=0&at=0&c=2741&p=op&posid=op_iphone_1&loc=Unknown&adstyle=open&ac=5487&ad=54962&pt=12621&b=417762&bk=117199509&pagetype=2&spead=0&rtm=__TIME__",
                                    "time": 0,
                                    "event": 1,
                                    "tag": "sohu"
                                },
                                {
                                    "url": "http://mmg.aty.sohu.com/pvlog?du=0&rt=1700032799115_6559_10.33.8.134_15_15&spead=0&plat=3&sver=9.9.20&poid=1&adplat=2&prot=json&protv=3.0&build=com.sohu.inhouse.iphonevideo&appid=tv&adoriginal=sohu&sdkVersion=15.9.1&offline=0&density=2.000000&displayMetrics=375*667&islocaltv=0&bt=20231115&endtime=20231231&ad=54962&b=417762&bk=117199509&pagetype=2&islocaltv=0&seq=1&w=1080&h=1920&wdbn=1080&hgbn=1920&cheattype=0&sperotime=1700032799&site=1&template=video&platsource=tv&indexip=adveng-retrvl-qa.ns-adveng-qa.svc.cluster.local:60111&backtest=ctr_cheat,pacing_ad_alloc_a,exp_nobidfloor,pdb_load_a,pdb_opt_a&ispgc=0&impressionid=7528c6f1f2089fe9a5e9dc4a70456d2d&scope=0&flightid=36609765&from=tvssp&advertiserid=11635&encd=92I3jLba%2FU8Tivxo0cfnxsGaxS0pwzAx9oO%2FNuFkHj6UXrQcMXwZW%2F0NPfH2QwiybpqwJqyftA1LozHeFj61jqs3U07L6anVRF%2FRZlASkCbNExR6QnM0%2FhhbC6TXvdkQKcwTUx05wkGgkhcFBO4yJio6hpIRGtcKXue2Wp76oByPpYD%2F2u1cdme7H%2FZExrh5IWzwb1ruZFkNChV%2FEs7QlZ0vrzJ8c260E6ngocShU1hjNZCMri4e8lWczTGrGTElL20lPoIfsUG6D8JNeBZ%2BZm%2Bqww%2Bsyd1D50tHcbOw5GOHOpFk1IhAna8%2FRm8cCbJMiCiUTpDYLZuE0c96iGqBYnqU%2BtSgIugMekH2yrTpx9iPpAYtbRVK7C8JPrX1sYPAexQRUikYg%2F0ddLYFyMPw2C1WR9fKvY6VpnfXOzerIgfSv%2BiKEzVUvn2igUimxsyVmb0ZVAKQBgAenHsrZP6JO6U20yI%3D&err=[ERRORCODE]&at=0&c=2741&p=op&posid=op_iphone_1&loc=Unknown&adstyle=open&ac=5487&ad=54962&pt=12621&b=417762&bk=117199509&pagetype=2&spead=0&eventtype=feedback&feedbackreason=__FEEDBACKCODE__",
                                    "event": 4,
                                    "tag": "sohu"
                                },
                                {
                                    "url": "http://mmg.aty.sohu.com/pvlog?&err=[ERRORCODE]&vp=[SKIPTIME]&du=0&rt=1700032799115_6559_10.33.8.134_15_15&spead=0&plat=3&sver=9.9.20&poid=1&adplat=2&prot=json&protv=3.0&build=com.sohu.inhouse.iphonevideo&appid=tv&adoriginal=sohu&sdkVersion=15.9.1&offline=0&density=2.000000&displayMetrics=375*667&islocaltv=0&bt=20231115&endtime=20231231&ad=54962&b=417762&bk=117199509&pagetype=2&islocaltv=0&seq=1&w=1080&h=1920&wdbn=1080&hgbn=1920&cheattype=0&sperotime=1700032799&site=1&template=video&platsource=tv&indexip=adveng-retrvl-qa.ns-adveng-qa.svc.cluster.local:60111&backtest=ctr_cheat,pacing_ad_alloc_a,exp_nobidfloor,pdb_load_a,pdb_opt_a&ispgc=0&impressionid=7528c6f1f2089fe9a5e9dc4a70456d2d&scope=0&flightid=36609765&from=tvssp&advertiserid=11635&encd=92I3jLba%2FU8Tivxo0cfnxsGaxS0pwzAx9oO%2FNuFkHj6UXrQcMXwZW%2F0NPfH2QwiybpqwJqyftA1LozHeFj61jqs3U07L6anVRF%2FRZlASkCbNExR6QnM0%2FhhbC6TXvdkQKcwTUx05wkGgkhcFBO4yJio6hpIRGtcKXue2Wp76oByPpYD%2F2u1cdme7H%2FZExrh5IWzwb1ruZFkNChV%2FEs7QlZ0vrzJ8c260E6ngocShU1hjNZCMri4e8lWczTGrGTElL20lPoIfsUG6D8JNeBZ%2BZm%2Bqww%2Bsyd1D50tHcbOw5GOHOpFk1IhAna8%2FRm8cCbJMiCiUTpDYLZuE0c96iGqBYnqU%2BtSgIugMekH2yrTpx9iPpAYtbRVK7C8JPrX1sYPAexQRUikYg%2F0ddLYFyMPw2C1WR9fKvY6VpnfXOzerIgfSv%2BiKEzVUvn2igUimxsyVmb0ZVAKQBgAenHsrZP6JO6U20yI%3D&ischarge=0&eventtype=skip&at=0&c=2741&p=op&posid=op_iphone_1&loc=Unknown&adstyle=open&ac=5487&ad=54962&pt=12621&b=417762&bk=117199509&pagetype=2&spead=0",
                                    "event": 12,
                                    "tag": "sohu"
                                }
                            ],
                            "deeplink_url": "openapp.jdmobile://virtual?params=%7B%22category%22%3A%22jump%22%2C%22des%22%3A%22m%22%2C%22url%22%3A%22http%3A%2F%2Fclickc.admaster.com.cn%2Fc%2Fa140250%2Cb4078143%2Cc1849%2Ci0%2Cm101%2C8a2%2C8b3%2C0iPUB_444326%2Ch1700032799115_6559_10.33.8.134_15_15_171782290%2Cuhttps%253A%252F%252Fccc-x.jd.com%252Fdsp%252Fcl%253Fposid%253D1999%2526v%253D707%2526union_id%253D1000027279%2526pid%253D2248%2526tagid%253D109284%2526didmd5%253D%2526idfamd5%253D%2526did%253D__IMEIIMEI__%2526idfa%253D__IDFAIDFA__%2526to%253Dhttps%25253A%25252F%25252Fpro.m.jd.com%25252Fmall%25252Factive%25252FMtfv4iYJULmi7zTWrAGmnGidSeK%25252Findex.html%25253Fad_od%25253D1%22%2C%22m_param%22%3A%7B%22jdv%22%3A%22122270672%7Ckong%7Ct_1000027279_109284%7Czssc%7Cd36d13b9-61c4-4fdf-b7f2-11dbc28d14dd-p_1999-pr_2248-at_109284%22%7D%2C%22keplerID%22%3A%22kpl_jdjdtg00001054%22%2C%22keplerFrom%22%3A%221%22%2C%22kepler_param%22%3A%7B%22source%22%3A%22kepler-open%22%2C%22otherData%22%3A%7B%22mopenbp7%22%3A%22kpl_jdjdtg00001054%22%2C%22channel%22%3A%22b4dc3278288f4a25982ccdec07ebdc41%22%7D%7D%7D",
                            "creatives": {
                                "video": {
                                    "height": 1920,
                                    "content": "http://data.vod.itc.cn/?new=/7/59/uqnI4NE8JxrLU5U2VUzJUB.mp4&prod=ad&sig=am0eQrhcmb10QKl4-zCwdER97KFFdtE3",
                                    "duration": 20,
                                    "materialtype": "video/mp4",
                                    "width": 1080
                                }
                            },
                            "pos": 0,
                            "ext": {
                                "brandoverlay": 1,
                                "support_union": 1,
                                "clicktype": 1,
                                "expiretime": "1700063999000",
                                "hardflag": 3,
                                "ClickType": 1,
                                "opendelay": "20",
                                "deeplinkflag": 1,
                                "replaceable": 0,
                                "display_type": 0,
                                "excluded": 0
                            },
                            "pt": "open",
                            "click_monitor": [
                                {
                                    "url": "http://mmg.aty.sohu.com/goto?du=0&rt=1700032799115_6559_10.33.8.134_15_15&spead=0&plat=3&sver=9.9.20&poid=1&adplat=2&prot=json&protv=3.0&build=com.sohu.inhouse.iphonevideo&appid=tv&adoriginal=sohu&sdkVersion=15.9.1&offline=0&density=2.000000&displayMetrics=375*667&bt=20231115&endtime=20231231&ad=54962&b=417762&bk=117199509&pagetype=2&islocaltv=0&seq=1&w=1080&h=1920&wdbn=1080&hgbn=1920&cheattype=0&sperotime=1700032799&site=1&template=video&platsource=tv&indexip=adveng-retrvl-qa.ns-adveng-qa.svc.cluster.local:60111&backtest=ctr_cheat,pacing_ad_alloc_a,exp_nobidfloor,pdb_load_a,pdb_opt_a&ispgc=0&impressionid=7528c6f1f2089fe9a5e9dc4a70456d2d&scope=0&flightid=36609765&from=tvssp&advertiserid=11635&encd=92I3jLba%2FU8Tivxo0cfnxsGaxS0pwzAx9oO%2FNuFkHj6UXrQcMXwZW%2F0NPfH2QwiybpqwJqyftA1LozHeFj61jqs3U07L6anVRF%2FRZlASkCbNExR6QnM0%2FhhbC6TXvdkQKcwTUx05wkGgkhcFBO4yJio6hpIRGtcKXue2Wp76oByPpYD%2F2u1cdme7H%2FZExrh5IWzwb1ruZFkNChV%2FEs7QlZ0vrzJ8c260E6ngocShU1hjNZCMri4e8lWczTGrGTElL20lPoIfsUG6D8JNeBZ%2BZm%2Bqww%2Bsyd1D50tHcbOw5GOHOpFk1IhAna8%2FRm8cCbJMiCiUTpDYLZuE0c96iGqBYnqU%2BtSgIugMekH2yrTpx9iPpAYtbRVK7C8JPrX1sYPAexQRUikYg%2F0ddLYFyMPw2C1WR9fKvY6VpnfXOzerIgfSv%2BiKEzVUvn2igUimxsyVmb0ZVAKQBgAenHsrZP6JO6U20yI%3D&err=[ERRORCODE]&dx=__DOWN_X__&dy=__DOWN_Y__&ux=__UP_X__&uy=__UP_Y__&at=0&c=2741&p=op&posid=op_iphone_1&loc=Unknown&adstyle=open&ac=5487&ad=54962&pt=12621&b=417762&bk=117199509&pagetype=2&spead=0&rtm=__TIME__",
                                    "event": 5,
                                    "tag": "sohu"
                                },
                                {
                                    "url": "http://mmg.aty.sohu.com/goto?du=0&rt=1700032799115_6559_10.33.8.134_15_15&spead=0&plat=3&sver=9.9.20&poid=1&adplat=2&prot=json&protv=3.0&build=com.sohu.inhouse.iphonevideo&appid=tv&adoriginal=sohu&sdkVersion=15.9.1&offline=0&density=2.000000&displayMetrics=375*667&bt=20231115&endtime=20231231&ad=54962&b=417762&bk=117199509&pagetype=2&islocaltv=0&seq=1&w=1080&h=1920&wdbn=1080&hgbn=1920&cheattype=0&sperotime=1700032799&site=1&template=video&platsource=tv&indexip=adveng-retrvl-qa.ns-adveng-qa.svc.cluster.local:60111&backtest=ctr_cheat,pacing_ad_alloc_a,exp_nobidfloor,pdb_load_a,pdb_opt_a&ispgc=0&impressionid=7528c6f1f2089fe9a5e9dc4a70456d2d&scope=0&flightid=36609765&from=tvssp&advertiserid=11635&encd=92I3jLba%2FU8Tivxo0cfnxsGaxS0pwzAx9oO%2FNuFkHj6UXrQcMXwZW%2F0NPfH2QwiybpqwJqyftA1LozHeFj61jqs3U07L6anVRF%2FRZlASkCbNExR6QnM0%2FhhbC6TXvdkQKcwTUx05wkGgkhcFBO4yJio6hpIRGtcKXue2Wp76oByPpYD%2F2u1cdme7H%2FZExrh5IWzwb1ruZFkNChV%2FEs7QlZ0vrzJ8c260E6ngocShU1hjNZCMri4e8lWczTGrGTElL20lPoIfsUG6D8JNeBZ%2BZm%2Bqww%2Bsyd1D50tHcbOw5GOHOpFk1IhAna8%2FRm8cCbJMiCiUTpDYLZuE0c96iGqBYnqU%2BtSgIugMekH2yrTpx9iPpAYtbRVK7C8JPrX1sYPAexQRUikYg%2F0ddLYFyMPw2C1WR9fKvY6VpnfXOzerIgfSv%2BiKEzVUvn2igUimxsyVmb0ZVAKQBgAenHsrZP6JO6U20yI%3D&err=[ERRORCODE]&dx=__DOWN_X__&dy=__DOWN_Y__&ux=__UP_X__&uy=__UP_Y__&at=0&c=2741&p=op&posid=op_iphone_1&loc=Unknown&adstyle=open&ac=5487&ad=54962&pt=12621&b=417762&bk=117199509&pagetype=2&spead=0&eventtype=deeplink",
                                    "event": 10,
                                    "tag": "sohu"
                                }
                            ],
                            "template": "",
                            "landing_url": "http://www.baidu.com"
                        }
                    ]
                }
            ],
            "version": 3,
            "impid": "ssp-app-qa-686f5d9c87-566rs000000126554711f0faf_cl"
        }

print(json.dumps(JsonHandle.get_target_result(res)))