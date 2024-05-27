"""
Author: John Du

File: model_structure.py
Description: Wrapper functions for calling APIs.
"""
import json
import logging
import requests
from requests.exceptions import RequestException
from log_utils import *

LogUtils.setup_logging()

def get_model_info(model_name, parameters=None):
    """
    获取模型信息。

    参数:
    - model_name: 模型名称。

    返回:
    - 一个包含模型信息的字典。
    """
    # 读取model_parameters.json文件获取所有模型参数
    with open('model_info.json', 'r') as file:
        model_info_dict = json.load(file)
    
    # 根据模型名称查找参数，如果不存在则返回默认模型llama3的参数
    model_info = {}
    if model_name in model_info_dict:
        model_info = model_info_dict[model_name]
    else:
        model_info = model_info["llama3_8B"]
    
    # 更新参数
    if parameters is not None:
        model_info = update_model_parameters(model_info, parameters)
    
    return model_info

    
def update_model_parameters(model_info, parameters):
    """
    更新或添加模型参数。

    参数:
    - model_info: 包含模型参数信息的字典。
    - parameters: 一个字典，包含要更新或添加的参数键值对。

    返回:
    - 更新后的model_info字典。
    """

    # 使用集合操作来找出需要更新或添加的键
    keys_to_update = set(parameters.keys()) & set(model_info["parameters"].keys())
    keys_to_add = set(parameters.keys()) - set(model_info["parameters"].keys())

    # 添加、更新存在的键
    for key in keys_to_update + keys_to_add:
        model_info["parameters"][key] = parameters.get(key, model_info["parameters"].get(key))

    return model_info

def model_request(model_info, prompt):
    
    if model_info["model"] == "llama3":
        model_url = model_info["url"]
        try:
            response = requests.post(model_url, json={"model": model_info["model"], "prompt": prompt, **{k: v for k, v in model_info.items() if k in ["parameters"]}})
            return response.json()
        except RequestException as e:
            logging.error(f'Error occurred while making a request to {model_url}: {e}')
            return "REQUEST_FAILED"

    elif model_info["model"] == "gpt4":
        model_url = model_info["url"]
        return model_url


def safe_generate_response(model_name,
                           prompt, 
                           parameters=None,
                           repeat=5,
                           fail_safe_response="error",
                           func_validate=None,
                           func_clean_up=None): 

    logging.info(f'prompt: {prompt}')

    # 获取模型信息
    model_info = get_model_info(model_name, parameters)

    # 更新模型参数
    if parameters is not None:
        model_info = update_model_parameters(model_info)

    logging.info(f'model_info: {model_info}')

    # 请求模型生成结果
    for i in range(repeat):
        try:
            model_response = model_request(model_info, prompt)
            if func_validate(model_response, prompt=prompt): 
                response_value = func_clean_up(model_response, prompt=prompt)

                logging.info(f'repeat count: {i}: {model_response}')

                return response_value
        except:
            pass

    logging.error("FAIL SAFE TRIGGERED")

    return fail_safe_response


def get_embedding(text, model="nomic-embed-text"):
    text = text.replace("\n", " ")
    if not text: 
        text = "this is blank"

    model_info = get_model_info(model)
    try:
        response = requests.post(model_info["url"], json={"model": model, "prompt": text})
        return response.json()
    except RequestException as e:
        logging.error(f'Error occurred while making a request to {model_info["url"]}: {e}')
        return "REQUEST_FAILED"


def generate_prompt(curr_input, prompt_lib_file): 
  """
  Takes in the current input (e.g. comment that you want to classifiy) and 
  the path to a prompt file. The prompt file contains the raw str prompt that
  will be used, which contains the following substr: !<INPUT>! -- this 
  function replaces this substr with the actual curr_input to produce the 
  final promopt that will be sent to the GPT3 server. 
  ARGS:
    curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                INPUT, THIS CAN BE A LIST.)
    prompt_lib_file: the path to the promopt file. 
  RETURNS: 
    a str prompt that will be sent to OpenAI's GPT server.  
  """
  if type(curr_input) == type("string"): 
    curr_input = [curr_input]
  curr_input = [str(i) for i in curr_input]

  f = open(prompt_lib_file, "r")
  prompt = f.read()
  f.close()
  for count, i in enumerate(curr_input):   
    prompt = prompt.replace(f"!<INPUT {count}>!", i)
  if "<commentblockmarker>###</commentblockmarker>" in prompt: 
    prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
  return prompt.strip()