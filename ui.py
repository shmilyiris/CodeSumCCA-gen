from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QComboBox, QTextEdit, QProgressBar, QCheckBox,
    QVBoxLayout, QHBoxLayout, QListWidget, QGroupBox, QFormLayout, QDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

from method.construct_prompts import construct_prompts
from method.extract_semantic_features import extract_semantic_features
from method.generate_documents import generate_document_parts
from method.load_code_module import load_code_module


class GenerationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文档生成进度")
        self.setModal(True)  # 设置为模态对话框
        self.resize(600, 400)
        layout = QVBoxLayout()

        # 进度条与步骤显示
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("当前步骤: 等待开始")
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        # 日志显示区域
        log_group = QGroupBox("生成日志")
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        log_layout = QVBoxLayout()
        log_layout.addWidget(self.log_box)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 结果预览区域
        result_group = QGroupBox("生成结果预览")
        self.result_preview = QTextEdit()
        self.result_preview.setReadOnly(True)
        self.result_preview.setFixedHeight(200)  # 固定高度
        self.result_preview.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 自动滚动条
        result_layout = QVBoxLayout()
        result_layout.addWidget(self.result_preview)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        # 保存按钮
        self.save_btn = QPushButton("保存文档")
        self.save_btn.clicked.connect(self.save_document)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def update_status(self, step, percent):
        self.status_label.setText(f"当前步骤: {step}")
        self.progress_bar.setValue(percent)

    def append_log(self, message):
        self.log_box.append(message)

    def set_result(self, text):
        self.result_preview.setPlainText(text)

    def save_document(self):
        # 实现保存逻辑
        pass


class DocumentGeneratorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('resource/figures/code.png'))
        self.setWindowTitle("Java代码文档生成器")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 模型选择与API Key
        model_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.addItems(["ChatGPT", "Qwen", "Claude"])
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("请输入API Key")
        model_layout.addWidget(QLabel("模型选择:"))
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(QLabel("API Key:"))
        model_layout.addWidget(self.api_key_input)
        layout.addLayout(model_layout)

        # 项目目录选择（水平布局）
        project_layout = QHBoxLayout()
        project_label = QLabel("项目目录:")
        project_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.project_path = QLineEdit()
        self.project_path.setPlaceholderText("请选择项目根目录")
        self.project_path.setMinimumWidth(600)  # 设置最小宽度
        project_btn = QPushButton("浏览目录")
        project_btn.clicked.connect(self.select_project_dir)
        project_btn.setFixedWidth(100)  # 固定按钮宽度

        project_layout.addWidget(project_label)
        project_layout.addWidget(self.project_path)
        project_layout.addWidget(project_btn)

        layout.addLayout(project_layout)

        # 关键文件添加（可选）
        self.key_files_list = QListWidget()
        key_file_btn = QPushButton("添加关键文件")
        key_file_btn.clicked.connect(self.add_key_files)
        layout.addWidget(QLabel("关键文件（可选）:"))
        layout.addWidget(self.key_files_list)
        layout.addWidget(key_file_btn)

        # 生成内容勾选区
        content_group = QGroupBox("生成模块选择")
        content_layout = QHBoxLayout()
        self.content_options = {
            "global_intro": QCheckBox("Global Introduction"),
            "module_intro": QCheckBox("Module Introduction"),
            "installation": QCheckBox("Installation"),
            "prerequisites": QCheckBox("Prerequisites"),
            "use_cases": QCheckBox("Use Cases"),
            "debug_suggestions": QCheckBox("Debug Suggestions"),
            "license": QCheckBox("License")
        }
        for opt in self.content_options.values():
            content_layout.addWidget(opt)
        content_group.setLayout(content_layout)
        layout.addWidget(content_group)

        # 风格设置区域优化
        style_group = QGroupBox("文档风格配置")
        style_layout = QHBoxLayout()

        # 篇幅选择
        length_label = QLabel("篇幅:")
        length_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.length_combo = QComboBox()
        self.length_combo.addItems(["极简", "普通", "详细"])
        self.length_combo.setFixedWidth(100)

        # 格式选择
        format_label = QLabel("格式:")
        format_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["默认", "Markdown", "LaTeX"])
        self.format_combo.setFixedWidth(100)

        # 风格选择
        style_label = QLabel("风格:")
        style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.style_combo = QComboBox()
        self.style_combo.addItems(["学术化", "工程化", "新用户友好"])
        self.style_combo.setFixedWidth(120)

        # 布局组装
        style_layout.addWidget(length_label)
        style_layout.addWidget(self.length_combo)
        style_layout.addWidget(format_label)
        style_layout.addWidget(self.format_combo)
        style_layout.addWidget(style_label)
        style_layout.addWidget(self.style_combo)
        style_layout.addStretch()

        style_group.setLayout(style_layout)
        layout.addWidget(style_group)

        # 自定义Prompt
        self.custom_prompt = QTextEdit()
        self.custom_prompt.setPlaceholderText("可选的自定义Prompt（500字以内）")
        layout.addWidget(QLabel("自定义Prompt:"))
        layout.addWidget(self.custom_prompt)

        # 开始生成按钮
        self.start_btn = QPushButton("开始生成")
        self.start_btn.clicked.connect(self.start_generation)
        layout.addWidget(self.start_btn)

        self.setLayout(layout)

    def select_project_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择项目根目录")
        if dir_path:
            self.project_path.setText(dir_path)

    def add_key_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择关键文件")
        self.key_files_list.addItems(files)

    def start_generation(self):
        # 启动后台线程执行生成任务
        self.dialog = GenerationDialog(self)

        thread = QThread()
        worker = GenerationWorker(self.get_config())
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress_update.connect(self.dialog.update_status)
        worker.log_update.connect(self.dialog.append_log)
        worker.result_ready.connect(self.dialog.set_result)
        worker.finished.connect(thread.quit)

        thread.start()
        self.dialog.exec_()  # 阻塞直到对话框关闭


    def get_config(self):
        return {
            "method": self.model_combo.currentText(),
            "api_key": self.api_key_input.text(),
            "project_dir": self.project_path.text(),
            "key_files": [self.key_files_list.item(i).text() for i in range(self.key_files_list.count())],
            "content_options": {k: v.isChecked() for k, v in self.content_options.items()},
            "length": self.length_combo.currentText(),
            "format": self.format_combo.currentText(),
            "custom_prompt": self.custom_prompt.toPlainText()
        }

    def update_progress(self, step, percent):
        self.status_label.setText(f"当前步骤: {step}/4")
        self.progress_bar.setValue(percent)

    def append_log(self, message):
        self.log_box.append(message)

    def show_result(self, result):
        self.result_preview.setPlainText(result)

    def save_document(self):
        # 实现保存功能
        pass


class GenerationWorker(QThread):
    progress_update = pyqtSignal(int, int)
    log_update = pyqtSignal(str)
    result_ready = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            # Step 1: 源代码载入
            self.log_update.emit("Step 1: 载入源代码...")
            repo_name = load_code_module(self.config["project_dir"])
            self.progress_update.emit(1, 25)

            # Step 2: 代码语义提炼
            self.log_update.emit("Step 2: 语义提炼...")
            semantic_features = extract_semantic_features(repo_name, self.config)
            self.progress_update.emit(2, 50)

            # Step 3: Prompt整合
            self.log_update.emit("Step 3: 构建Prompt...")
            prompts = construct_prompts(semantic_features, self.config)
            self.progress_update.emit(3, 75)

            # Step 4: 结果生成
            self.log_update.emit("Step 4: 生成文档...")
            final_document = generate_document_parts(prompts, self.config)
            self.progress_update.emit(4, 100)

            # 返回结果
            self.result_ready.emit(final_document)

        except Exception as e:
            self.log_update.emit(f"Error: {str(e)}")


# 启动应用
if __name__ == '__main__':
    app = QApplication([])
    ui = DocumentGeneratorUI()
    ui.show()
    app.exec_()
