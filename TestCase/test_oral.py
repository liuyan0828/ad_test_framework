"""
-*- coding: utf-8 -*-
@Time : 2024/6/5
@Author : liuyan
@function :
"""
import pytest
from main import project_path
from utils.ReadYaml import read_yaml_files
from utils.readExpectedResult import *
from libs.GetAdConf import *
from libs.checkResult import *


PATH = project_path + '/script/oral'
case_dict = read_yaml_files(PATH)


@allure.feature("聚享片头")
class Test_Ad_Open():
    @allure.story("1、校验非空广告 2、校验配置是否同mango配置一致 3、校验返回的lineid与ad 4、完全校验")
    # 重试10次间隔1s；3次中只要有一次成功case即成功
    @pytest.mark.flaky(reruns=10, reruns_delay=1)
    @pytest.mark.parametrize("case_data", case_dict[0], ids=case_dict[1])
    def test_ad_config(self, case_data, api_response):
        """

        :param case_data: 测试用例
        :param api_response: 请求返回数据
        :function: 校验mango配置是否一致
        """
        allure.title(f"{case_data}")
        check_adtype(api_response)
        payload = case_data['payload']
        mango_conf = GetAdConf(payload)
        if mango_conf.get_adtemplate() != "open_customize_click":
            check_and_assert(mango_conf.get_adtemplate, api_response, '$..template', "返回的template与配置不一致",
                             "res未下发template字段")
        check_and_assert(mango_conf.get_triggertype, api_response, '$..display_type', "返回的点击触发类型与配置不一致",
                         "mango配置了点击触发类型但实际未下发")
        check_and_assert(mango_conf.get_isdeeplink, api_response, '$..deeplinkflag', "返回的是否deeplink与配置不一致",
                         "mango配置了是否deeplink但实际未下发")
        check_and_assert(mango_conf.get_buttontext,  api_response, '$..buttontxt.content', "返回的点击按钮文案与配置不一致",
                         "mango配置了按钮文案但实际未下发")
        check_and_assert(mango_conf.get_imagetitle,  api_response, '$..title.content', "返回的图片标题与配置不一致",
                         "mango配置了图片标题但实际未下发")
        check_and_assert(mango_conf.get_imagesubtitle,  api_response, '$..advertiser.content', "返回的广告主来源与配置不一致",
                         "mango配置了广告主来源但实际未下发")
        check_redirect(mango_conf, api_response)
        expected_request = case_data['check']['expected_request']
        if isinstance(expected_request, str):
            _path = PATH + '/' + case_data['info']
            expected_request = read_json(case_data['info'], expected_request, _path)
        check_lineid(api_response, expected_request)
        check_returned_data(api_response, expected_request)
