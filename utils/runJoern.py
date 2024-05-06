import os
import sys
import subprocess
import glob

sys.path.append("..")

from utils.config import JOERN_PARSE_RUN, RUN_ENV


def generateCPG(target_dir: str):
    '''
    生成CPG
    :param target_dir: 需要解析的源码路径
    :return:
    '''
    if not os.path.exists(target_dir):
        return False, None, f"path {target_dir} is not exist", None
    res = subprocess.run(args=["bash", JOERN_PARSE_RUN, target_dir], capture_output=True, env=RUN_ENV)
    if res.returncode != 0:
        msg = res.stderr.decode(encoding='utf8')
        # print(f"error msg: {msg}")
        return False, None, f"generate cpg err, error msg:{msg}", None
    print("Parse CPG successfully.")
    all_c_files_list = glob.glob(pathname=f"{target_dir}/**/*.c", recursive=True)
    abs_c_files_list = [os.getcwd()+os.sep+"parsed"+item for item in all_c_files_list]
    # print(abs_c_files_list)
    return True, abs_c_files_list, "", os.getcwd()+os.sep+"parsed"


def delete_target_dir(target_dir: str):
    if not os.path.exists(target_dir):
        return True
    else:
        res = subprocess.run(f'rm -rf {target_dir}', shell=True)
        if res.returncode != 0:
            print(res.stderr.decode('utf8'))
        return res.returncode == 0


if __name__ == '__main__':
    # generateCPG(target_dir="/root/my_c_tests")

    # data = pd.read_csv("parsed/root/my_c_tests/fff/b.c/nodes.csv", sep='\t')
    # function_start_list = data[data['type'] == "Function"].index.to_list()
    # function_start_list.append(len(data))
    # for start, end in zip(function_start_list[:-1], function_start_list[1:]):
    #     print(data[start: end])
    #     print("***********************")
    rm_res = delete_target_dir(target_dir='/root/PycharmProjects/flaskVulDetectProject/utils/parsed')
