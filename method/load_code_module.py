import subprocess


def load_code_module(project_dir: str) -> str:
    """
    输入: 项目根目录
    输出: 解析后的JSON数据（包含类签名、成员变量、方法信息、依赖图等）
    """

    jar_path = '../model/CodeSumCCA-javaparser.jar'
    command = ["java", "-jar", jar_path, project_dir]

    subprocess.run(command, capture_output=True, text=True)

    return project_dir.split('/')[-1]