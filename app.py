import json
import time
from flask import Flask
from flask import request
from flask_caching import Cache
from pathlib import Path
from peft import AutoPeftModelForCausalLM, PeftModelForCausalLM
from transformers import (
    AutoModelForCausalLM,
    AutoModel,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)

app = Flask(__name__)
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
cache = Cache(app=app, config=config)

def _resolve_path(path):
    return Path(path).expanduser().resolve()


def load_project_model_and_tokenizer(model_dir):
    model_dir = _resolve_path(model_dir)
    if (model_dir / 'adapter_config.json').exists():
        model = AutoPeftModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device_map='auto'
        )
        tokenizer_dir = model.peft_config['default'].base_model_name_or_path
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device_map='auto'
        )
        tokenizer_dir = model_dir
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_dir, trust_remote_code=True
    )
    return model, tokenizer


# File summary model
FILE_MODEL_PATH = '/home/LAB/guanz/gz_graduation/code_embedding_pretrained_model/chatglm3-6b-128k'
file_tokenizer = AutoTokenizer.from_pretrained(FILE_MODEL_PATH, trust_remote_code=True)
file_model = AutoModel.from_pretrained(FILE_MODEL_PATH, trust_remote_code=True).half().cuda()
file_sequence_max_length = file_model.config.seq_length
print('File Model Max Sequence Length {}'.format(file_sequence_max_length))
file_model = file_model.eval()

# Project summary model
PROJECT_MODEL_PATH = '/home/LAB/guanz/gz_graduation/chatglm_finetune/output_hierarchy/checkpoint-1000/'
project_model, project_tokenizer = load_project_model_and_tokenizer(PROJECT_MODEL_PATH)
project_sequence_max_length = project_model.config.seq_length
print('Project Model Max Sequence Length {}'.format(project_sequence_max_length))


def file_cache_key():
    with app.app_context():
        cache_key = request.form.get("fileName")
    return cache_key


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/file', methods=['POST'])
@cache.cached(timeout=60*60, key_prefix=file_cache_key)
def get_file_summary():
    start_time = time.time()
    fileName = request.form.get("fileName")
    repoName = request.form.get("repoName")
    fileContext = request.form.get("context")
    question = 'Please help me write a one-sentence summary of the java class file {} from the open-source project named {}. The summary should capture the overall functionality of the file in no longer than 30 words, without describing each function individually. The code is\n\n'.format(
        fileName,
        repoName
    )
    question = question + fileContext
    if len(file_tokenizer.tokenize(question)) >= file_sequence_max_length:
        print('###### File {} has too long code.'.format(fileName))
        return json.dumps({'code': 401, 'msg': 'Code length is too long.'})
    response, history = file_model.chat(file_tokenizer, question, history=[])
    end_time = time.time()
    print('###### File {} summary complete use {} s'.format(fileName, end_time - start_time))
    return json.dumps({'code': 200, 'msg': 'File summary complete.', 'res': response})


@app.route('/project', methods=['POST'])
def get_project_summary():
    start_time = time.time()
    repoName = request.form.get("repoName")
    # 用一个map或者list来装，先测试一下
    summaryJson = request.form.get("summaries")
    summaryObject = json.loads(summaryJson)

    hierarchy_object = {}
    file_keys = summaryObject.keys()
    for file in file_keys:
        if file.rfind('.') != -1:
            package_name = file[:file.rfind('.')]
            file_name = file[file.rfind('.') + 1:]
        else:
            package_name = repoName
            file_name = file
        if package_name not in hierarchy_object.keys():
            hierarchy_object[package_name] = {}
        file_summary = summaryObject[file]
        file_name += ".java"
        # 加上package和file的信息
        hierarchy_object[package_name][file_name] = file_summary
    hierarchy_object_str = str(hierarchy_object)
    prompt = 'The open-source project {} has a hierarchical JSON string, containing each package along with its most important files and file summaries. Please give me an introduction about the project based on the JSON below. \n'.format(
        repoName)
    prompt += hierarchy_object_str
    print(prompt)
    if len(project_tokenizer.tokenize(prompt)) >= project_sequence_max_length:
        print('###### Prompt of {} has too many tokens.'.format(repoName))
        return json.dumps({'code': 401, 'msg': 'Prompt length is too long.'})
    response, _ = project_model.chat(project_tokenizer, prompt)
    end_time = time.time()
    print('###### Project {} summary complete use {} s'.format(repoName, end_time - start_time))
    return json.dumps({'code': 200, 'msg': 'Project summary complete.', 'res': response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
