import json
import time
from flask import Flask
from flask import request
from transformers import AutoTokenizer, AutoModel

app = Flask(__name__)

FILE_MODEL_PATH = '/home/LAB/guanz/gz_graduation/code_embedding_pretrained_model/chatglm3-6b-128k'
file_tokenizer = AutoTokenizer.from_pretrained(FILE_MODEL_PATH, trust_remote_code=True)
file_model = AutoModel.from_pretrained(FILE_MODEL_PATH, trust_remote_code=True).half().cuda()
sequence_max_length = file_model.config.seq_length
print('Model Max Sequence Length {}'.format(sequence_max_length))
file_model = file_model.eval()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/file', methods=['POST'])
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
    if len(file_tokenizer.tokenize(question)) >= sequence_max_length:
        print('###### File {} has too long code.'.format(fileName))
        return json.dumps({'code': 401, 'msg': 'Code length is too long.'})
    response, history = file_model.chat(file_tokenizer, question, history=[])
    end_time = time.time()
    print('###### File {} summary complete use {} s'.format(fileName, end_time - start_time))
    return json.dumps({'code': 200, 'msg': 'File summary complete.', 'res': response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
