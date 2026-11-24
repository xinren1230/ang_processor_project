# ANG Processor · ANG 文件欧拉角处理工具

[English](#english) | [中文](#中文)

---

## English

A PyQt5 desktop tool for transforming the Euler angles in EBSD `.ang` files.

### Features

- **File handling**: load an ANG file and save the processed result
- **Euler angle transforms**:
  - Horizontal flip
  - Vertical flip
  - Rotation about the Z axis (custom angle)
- **Preview**: see the crystal orientation of a chosen point before and after the transform
- **Reset**: undo all transforms with one click

### Download (no Python needed)

Grab `ANG_Processor.exe` from the [Releases page](https://github.com/xinren1230/ang_processor_project/releases) and double-click it. Windows only.

### Run from source

**One-click:** double-click `setup_and_run.bat`. It checks Python, creates a virtual environment, installs the dependencies and starts the program.

**Step by step:** run `setup_env.bat` once to set up the environment, then `run.bat` to start the program.

**Manual:**

```bash
python -m venv venv
# Windows
venv\Scripts\activate.bat
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
python ang_processor.py
```

### Usage

1. Click "选择ANG文件" (Select ANG file) and pick the file to process.
2. Apply transforms:
   - **Horizontal flip** mirrors the X coordinates and adjusts the Euler angles accordingly.
   - **Vertical flip** mirrors the Y coordinates and adjusts the Euler angles accordingly.
   - **Z rotation**: set the angle, then click "应用Z轴旋转" (Apply Z rotation).
3. Preview: choose a point in "预览点索引" (Preview point index); the left view shows the grain before the transform, the right view after.
4. Click "保存ANG文件" (Save ANG file) to write the result.

### ANG file format

Standard ANG format, one point per line: `X Y IQ CI Phase Phi1 PHI Phi2` (coordinates, image quality, confidence index, phase ID, Euler angles in degrees). See `example.ang`.

### Notes

- Lines starting with `#` are treated as comments and skipped.
- Transforms follow standard crystallographic conventions.
- All angles are normalized to 0–360°.

---

## 中文

这是一个基于 PyQt5 的图形界面工具，用于处理 EBSD `.ang` 文件的欧拉角变换。

### 功能特性

- **文件操作**：选择并加载 ANG 文件，保存处理后的 ANG 文件
- **欧拉角变换**：
  - 水平翻转
  - 垂直翻转
  - Z 轴旋转（可自定义角度）
- **预览功能**：实时预览变换前后指定点的晶粒取向
- **重置功能**：一键重置所有变换

### 直接下载（无需安装 Python）

在 [Releases 页面](https://github.com/xinren1230/ang_processor_project/releases) 下载 `ANG_Processor.exe`，双击即可运行（仅限 Windows）。

### 从源码运行

**一键运行：** 双击 `setup_and_run.bat`，脚本会自动检查 Python、创建虚拟环境、安装依赖并启动程序。

**分步操作：** 先运行 `setup_env.bat` 配置环境，之后用 `run.bat` 启动程序。

**手动安装：**

```bash
python -m venv venv
# Windows
venv\Scripts\activate.bat
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
python ang_processor.py
```

### 使用方法

1. 点击"选择ANG文件"，选择要处理的 ANG 文件。
2. 使用变换按钮进行欧拉角变换：
   - **水平翻转**：翻转 X 坐标并调整相应的欧拉角
   - **垂直翻转**：翻转 Y 坐标并调整相应的欧拉角
   - **Z 轴旋转**：设置旋转角度后点击"应用Z轴旋转"
3. 预览：在"预览点索引"中选择数据点，左侧显示变换前的晶粒，右侧显示变换后的晶粒。
4. 点击"保存ANG文件"保存结果。

### ANG 文件格式

支持标准 ANG 格式，每行为 `X Y IQ CI Phase Phi1 PHI Phi2`（坐标、图像质量、置信度指数、相编号、欧拉角，单位为度）。示例见 `example.ang`。

### 注意事项

- 以 `#` 开头的注释行会被自动跳过
- 欧拉角变换遵循标准的晶体学变换规则
- 所有角度会自动归一化到 0–360° 范围

---

## License · 许可证

[MIT](LICENSE) © 2026 Xinren Chen