import subprocess
import os


def load_code_module(project_dir: str) -> str:
    """
    输入: 项目根目录
    输出: 解析后的JSON数据位置（包含类签名、成员变量、方法信息、依赖图等）
    """

    jar_path = os.getcwd() + '/model/CodeSumCCA-javaparser-1.0-SNAPSHOT.jar'
    command = ["java", "-jar", jar_path, project_dir]

    subprocess.run(command, capture_output=True, text=True)

    return f"tmp/output/{project_dir.split('/')[-1]}"