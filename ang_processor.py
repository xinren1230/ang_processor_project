#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ANG文件欧拉角处理工具
支持视角翻转、Z轴旋转，并提供预览功能
"""

import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QLabel, 
                             QSpinBox, QGroupBox, QMessageBox, QGraphicsView, 
                             QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem,
                             QGraphicsLineItem, QGraphicsPolygonItem)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QPainter
import os
import math


class AngProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ang_data = None
        self.original_data = None
        self.file_path = None
        self.preview_point_index = 0
        self.original_header = []  # Store original file header information
        self.applied_operations = []  # Track applied transformations
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('ANG File Euler Angle Processor')
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)
        
        # Right preview area
        preview_panel = self.create_preview_panel()
        main_layout.addWidget(preview_panel, 2)
        
    def create_control_panel(self):
        """Create control panel"""
        panel = QGroupBox("Control Panel")
        layout = QVBoxLayout()
        
        # File operations
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        btn_open = QPushButton("Open ANG File")
        btn_open.clicked.connect(self.open_file)
        file_layout.addWidget(btn_open)
        
        btn_save = QPushButton("Save ANG File")
        btn_save.clicked.connect(self.save_file)
        btn_save.setEnabled(False)
        self.btn_save = btn_save
        file_layout.addWidget(btn_save)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Transformation operations
        transform_group = QGroupBox("Euler Angle Transformations")
        transform_layout = QVBoxLayout()
        
        btn_horizontal_mirror = QPushButton("Horizontal Mirror (y→-y)")
        btn_horizontal_mirror.clicked.connect(self.horizontal_mirror)
        btn_horizontal_mirror.setEnabled(False)
        self.btn_horizontal_mirror = btn_horizontal_mirror
        transform_layout.addWidget(btn_horizontal_mirror)
        
        btn_vertical_mirror = QPushButton("Vertical Mirror (x→-x)")
        btn_vertical_mirror.clicked.connect(self.vertical_mirror)
        btn_vertical_mirror.setEnabled(False)
        self.btn_vertical_mirror = btn_vertical_mirror
        transform_layout.addWidget(btn_vertical_mirror)
        
        # Z-axis rotation
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Z-axis Rotation Angle:"))
        self.rotation_spinbox = QSpinBox()
        self.rotation_spinbox.setRange(-180, 180)
        self.rotation_spinbox.setSuffix("°")
        self.rotation_spinbox.setValue(0)
        rotation_layout.addWidget(self.rotation_spinbox)
        
        btn_rotate = QPushButton("Apply Z-axis Rotation")
        btn_rotate.clicked.connect(self.z_axis_rotate)
        btn_rotate.setEnabled(False)
        self.btn_rotate = btn_rotate
        rotation_layout.addWidget(btn_rotate)
        
        transform_layout.addLayout(rotation_layout)
        
        btn_reset = QPushButton("Reset Transformations")
        btn_reset.clicked.connect(self.reset_transform)
        btn_reset.setEnabled(False)
        self.btn_reset = btn_reset
        transform_layout.addWidget(btn_reset)
        
        transform_group.setLayout(transform_layout)
        layout.addWidget(transform_group)
        
        # Preview control
        preview_group = QGroupBox("Preview Control")
        preview_control_layout = QVBoxLayout()
        
        preview_point_layout = QHBoxLayout()
        preview_point_layout.addWidget(QLabel("Preview Point Index:"))
        self.preview_spinbox = QSpinBox()
        self.preview_spinbox.setRange(0, 0)
        self.preview_spinbox.valueChanged.connect(self.update_preview)
        preview_point_layout.addWidget(self.preview_spinbox)
        preview_control_layout.addLayout(preview_point_layout)
        
        btn_update_preview = QPushButton("Update Preview")
        btn_update_preview.clicked.connect(self.update_preview)
        btn_update_preview.setEnabled(False)
        self.btn_update_preview = btn_update_preview
        preview_control_layout.addWidget(btn_update_preview)
        
        preview_group.setLayout(preview_control_layout)
        layout.addWidget(preview_group)
        
        # Information display
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Waiting for file to load...")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_preview_panel(self):
        """Create preview panel"""
        panel = QGroupBox("Preview")
        layout = QVBoxLayout()
        
        # 创建两个图形视图用于显示变换前后的晶粒
        preview_layout = QHBoxLayout()
        
        # Before transformation
        before_group = QGroupBox("Before")
        before_layout = QVBoxLayout()
        self.before_view = QGraphicsView()
        self.before_scene = QGraphicsScene()
        self.before_view.setScene(self.before_scene)
        self.before_view.setMinimumSize(300, 300)
        # 设置自动适应场景大小和抗锯齿
        self.before_view.setRenderHint(QPainter.Antialiasing)
        before_layout.addWidget(self.before_view)
        before_group.setLayout(before_layout)
        preview_layout.addWidget(before_group)
        
        # After transformation
        after_group = QGroupBox("After")
        after_layout = QVBoxLayout()
        self.after_view = QGraphicsView()
        self.after_scene = QGraphicsScene()
        self.after_view.setScene(self.after_scene)
        self.after_view.setMinimumSize(300, 300)
        # 设置自动适应场景大小和抗锯齿
        self.after_view.setRenderHint(QPainter.Antialiasing)
        after_layout.addWidget(self.after_view)
        after_group.setLayout(after_layout)
        preview_layout.addWidget(after_group)
        
        layout.addLayout(preview_layout)
        panel.setLayout(layout)
        return panel
    
    def open_file(self):
        """Open ANG file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select ANG File", "", "ANG Files (*.ang);;All Files (*)")
        
        if file_path:
            try:
                # 初始化头部信息
                self.original_header = []
                self.ang_data = self.read_ang_file(file_path)
                
                # 验证数据完整性
                if len(self.ang_data['phi2']) == 0 or np.all(self.ang_data['phi2'] == 0):
                    # 如果Phi2全部为0，可能是读取问题
                    QMessageBox.warning(self, "Warning", 
                        f"Phi2 values may have issues.\n"
                        f"First point Phi2: {self.ang_data['phi2'][0] if len(self.ang_data['phi2']) > 0 else 'N/A'}\n"
                        f"Please check if the ANG file format is correct.")
                
                # 深拷贝原始数据
                self.original_data = {}
                for key in self.ang_data:
                    self.original_data[key] = self.ang_data[key].copy()
                self.file_path = file_path
                
                # 更新UI
                self.file_label.setText(f"File: {os.path.basename(file_path)}")
                self.btn_save.setEnabled(True)
                self.btn_horizontal_mirror.setEnabled(True)
                self.btn_vertical_mirror.setEnabled(True)
                self.btn_rotate.setEnabled(True)
                self.btn_reset.setEnabled(True)
                self.btn_update_preview.setEnabled(True)
                
                # 设置预览点范围
                num_points = len(self.ang_data['x'])
                if num_points == 0:
                    raise ValueError("File is empty or format is incorrect, no data read")
                
                self.preview_spinbox.setMaximum(max(0, num_points - 1))
                self.preview_spinbox.setValue(0)
                
                # Update information
                self.info_label.setText(
                    f"Loaded {num_points} data points\n"
                    f"X range: {self.ang_data['x'].min():.2f} - {self.ang_data['x'].max():.2f}\n"
                    f"Y range: {self.ang_data['y'].min():.2f} - {self.ang_data['y'].max():.2f}\n"
                    f"Phi1 range: {math.degrees(self.ang_data['phi1'].min()):.2f}° - {math.degrees(self.ang_data['phi1'].max()):.2f}°\n"
                    f"PHI range: {math.degrees(self.ang_data['phi'].min()):.2f}° - {math.degrees(self.ang_data['phi'].max()):.2f}°\n"
                    f"Phi2 range: {math.degrees(self.ang_data['phi2'].min()):.2f}° - {math.degrees(self.ang_data['phi2'].max()):.2f}°"
                )
                
                # Update preview
                self.update_preview()
                
                QMessageBox.information(self, "Success", f"Successfully loaded {num_points} data points")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read file:\n{str(e)}")
    
    def read_ang_file(self, file_path):
        """读取ANG文件"""
        data = {
            'x': [],
            'y': [],
            'iq': [],
            'ci': [],
            'phase': [],
            'phi1': [],
            'phi': [],
            'phi2': [],
            'sem': [],  # SEM列（如果存在）
            'fit': []   # Fit列（如果存在）
        }
        
        try:
            # 尝试多种编码方式，按优先级排序
            # latin-1可以读取任何字节，不会出错，优先使用
            encodings = ['latin-1', 'utf-8', 'cp1252', 'gbk', 'ascii']
            lines = None
            last_error = None
            
            for encoding in encodings:
                try:
                    # 使用errors='replace'来处理无法解码的字符
                    # 对于cp1252等编码，如果遇到无法解码的字节，使用replace模式
                    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                        lines = f.readlines()
                    # 如果成功读取，检查是否包含太多替换字符（可能编码不对）
                    # 对于latin-1，我们总是接受，因为它不会出错
                    if encoding == 'latin-1' or len(lines) > 0:
                        break
                except (UnicodeDecodeError, UnicodeError) as e:
                    last_error = e
                    # 如果遇到编码错误，继续尝试下一个编码
                    continue
                except Exception as e:
                    last_error = e
                    continue
            
            # 如果所有编码都失败，尝试二进制模式读取
            if lines is None:
                try:
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                    # 尝试检测编码或使用latin-1（可以读取任何字节）
                    try:
                        lines = raw_data.decode('utf-8', errors='replace').splitlines()
                    except:
                        lines = raw_data.decode('latin-1', errors='replace').splitlines()
                    # 转换回字符串列表
                    lines = [line + '\n' if isinstance(line, str) else line.decode('latin-1', errors='replace') + '\n' 
                            for line in lines]
                except Exception as e:
                    raise ValueError(f"Unable to read file, please check file encoding. Last error: {str(last_error) if last_error else str(e)}")
            
            if lines is None or len(lines) == 0:
                raise ValueError("File is empty or cannot be read")
            
            # 保存原始头部信息（注释行和标题行）
            header_lines = []
            data_lines = []
            in_data_section = False
            original_column_count = None  # 记录原始文件的列数
            
            for line in lines:
                original_line = line.rstrip('\n\r')
                line_stripped = original_line.strip()
                
                # 保存所有注释行和空行作为头部
                if not line_stripped or line_stripped.startswith('#'):
                    header_lines.append(original_line)
                    continue
                
                # 检查是否是列标题行
                if not in_data_section:
                    upper_line = line_stripped.upper()
                    if upper_line.startswith('X') or 'PHI' in upper_line or 'PHASE' in upper_line:
                        header_lines.append(original_line)
                        in_data_section = True
                        continue
                
                # 数据行
                if in_data_section or not any(c.isalpha() for c in line_stripped.split()[0] if line_stripped.split()):
                    data_lines.append(line_stripped)
                    in_data_section = True
                    # 记录第一行数据的列数（用于保存时判断格式）
                    if original_column_count is None:
                        parts = line_stripped.split()
                        if len(parts) > 0:
                            original_column_count = len(parts)
                            print(f"DEBUG: 检测到原始文件列数: {original_column_count}")
                    # 记录第一行数据的列数
                    if original_column_count is None:
                        parts = line_stripped.split()
                        if len(parts) > 0:
                            original_column_count = len(parts)
            
            # 解析数据行
            # TSL .ang 文件的标准列顺序：
            # phi1, Phi, phi2, x, y, IQ, CI, Phase, SEM, Fit
            parsed_count = 0
            for line_idx, line in enumerate(data_lines):
                parts = line.split()
                
                # 跳过空行
                if len(parts) == 0:
                    continue
                
                try:
                    # 标准TSL .ang格式：至少需要8列（phi1, Phi, phi2, x, y, IQ, CI, Phase）
                    # 可能有9列（加上Fit）或10列（加上SEM, Fit）
                    if len(parts) >= 8:
                        # 列顺序：phi1, Phi, phi2, x, y, IQ, CI, Phase, [SEM], Fit
                        phi1 = float(parts[0])
                        phi = float(parts[1])
                        phi2 = float(parts[2])
                        x = float(parts[3])
                        y = float(parts[4])
                        iq = float(parts[5])
                        ci = float(parts[6])
                        phase = int(float(parts[7]))  # 先转float再转int，处理小数形式的整数
                        
                        # 根据列数判断格式
                        if len(parts) == 10:
                            # 10列：phi1, Phi, phi2, x, y, IQ, CI, Phase, SEM, Fit
                            sem = float(parts[8])
                            fit = float(parts[9])
                        elif len(parts) == 9:
                            # 9列：phi1, Phi, phi2, x, y, IQ, CI, Phase, Fit (没有SEM)
                            sem = 0.0
                            fit = float(parts[8])
                        else:
                            # 8列：phi1, Phi, phi2, x, y, IQ, CI, Phase
                            sem = 0.0
                            fit = 100.0  # Fit默认值通常是100
                        
                        data['phi1'].append(phi1)
                        data['phi'].append(phi)
                        data['phi2'].append(phi2)
                        data['x'].append(x)
                        data['y'].append(y)
                        data['iq'].append(iq)
                        data['ci'].append(ci)
                        data['phase'].append(phase)
                        data['sem'].append(sem)
                        data['fit'].append(fit)
                        parsed_count += 1
                        
                        # 调试：打印前几行数据
                        if parsed_count <= 3:
                            print(f"DEBUG 行{line_idx+1}: 解析成功 - phi1={phi1:.2f}, Phi={phi:.2f}, phi2={phi2:.2f}, x={x:.2f}, y={y:.2f}, 列数={len(parts)}, SEM={sem}, Fit={fit}")
                    elif len(parts) >= 6:
                        # 最小格式：phi1, Phi, phi2, x, y, Phase（6列）
                        phi1 = float(parts[0])
                        phi = float(parts[1])
                        phi2 = float(parts[2])
                        x = float(parts[3])
                        y = float(parts[4])
                        phase = int(float(parts[5]))
                        
                        data['phi1'].append(phi1)
                        data['phi'].append(phi)
                        data['phi2'].append(phi2)
                        data['x'].append(x)
                        data['y'].append(y)
                        data['iq'].append(0.0)  # 默认值
                        data['ci'].append(0.0)  # 默认值
                        data['phase'].append(phase)
                        data['sem'].append(0.0)  # 默认值
                        data['fit'].append(100.0)  # 默认值
                        parsed_count += 1
                        
                        # 调试：打印前几行数据
                        if parsed_count <= 3:
                            print(f"DEBUG 行{line_idx+1}: 解析成功(6列) - phi1={phi1:.2f}, Phi={phi:.2f}, phi2={phi2:.2f}")
                    else:
                        # 列数不足，跳过
                        if line_idx < 5:
                            print(f"DEBUG 行{line_idx+1}: 列数不足 - 只有{len(parts)}列，需要至少6列, parts={parts}")
                        continue
                except (ValueError, IndexError) as e:
                    # 跳过无法解析的行
                    if line_idx < 5:  # 只打印前5行的错误
                        print(f"DEBUG 行{line_idx+1}: 解析失败 - {str(e)}, parts={parts[:10] if len(parts) > 10 else parts}")
                    continue
            
            # Check if data was read
            if len(data['x']) == 0:
                raise ValueError(
                    "No valid data read from file.\n"
                    "Please check if the file format is correct.\n"
                    "ANG file should contain: X Y IQ CI Phase Phi1 PHI Phi2\n"
                    f"Attempted to parse {len(data_lines)} lines, but found no valid data."
                )
            
            # Validate Phi2 data
            if len(data['phi2']) == 0:
                raise ValueError("Failed to read Phi2 data, please check ANG file format")
            
            if len(data['phi2']) != len(data['x']):
                raise ValueError(f"Phi2 data length ({len(data['phi2'])}) does not match X data length ({len(data['x'])})")
            
            # Check if all Phi2 values are 0 (may be a reading error)
            phi2_list = data['phi2']
            if len(phi2_list) > 0:
                phi2_nonzero = [v for v in phi2_list if abs(v) > 0.001]
                if len(phi2_nonzero) == 0:
                    print(f"Warning: All Phi2 values are 0 or close to 0, may be a reading format issue")
                    print(f"First 3 data points Phi2 values: {phi2_list[:3] if len(phi2_list) >= 3 else phi2_list}")
                else:
                    print(f"Reading complete: {len(data['x'])} data points")
                    # Euler angles in ANG files are in radians, convert to degrees for display
                    print(f"Phi2 range: {math.degrees(min(phi2_list)):.2f}° - {math.degrees(max(phi2_list)):.2f}°")
                    phi2_deg = [math.degrees(v) for v in (phi2_list[:3] if len(phi2_list) >= 3 else phi2_list)]
                    print(f"First 3 points Phi2 values (degrees): {phi2_deg}")
            
            # 转换为numpy数组
            for key in data:
                data[key] = np.array(data[key])
            
            # 保存头部信息供后续使用
            self.original_header = header_lines
            # 保存原始文件的列数（用于保存时判断格式）
            self.original_column_count = original_column_count
            
            return data
            
        except Exception as e:
            raise ValueError(f"读取ANG文件时出错: {str(e)}")
    
    def save_file(self):
        """Save ANG file"""
        if self.ang_data is None:
            QMessageBox.warning(self, "Warning", "No data to save. Please load an ANG file first.")
            return
        
        # 检查是否有变化
        has_changes = False
        if self.original_data is not None:
            # 比较原始数据和当前数据
            for key in ['x', 'y', 'phi1', 'phi', 'phi2']:
                if not np.array_equal(self.original_data[key], self.ang_data[key]):
                    has_changes = True
                    break
        
        if not has_changes and self.original_data is not None:
            reply = QMessageBox.question(
                self, "Confirm", 
                "Data has not changed. Save anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存ANG文件", "", "ANG Files (*.ang);;All Files (*)")
        
        if file_path:
            try:
                # 确保使用当前变换后的数据
                data_to_save = {}
                for key in self.ang_data:
                    data_to_save[key] = self.ang_data[key].copy()
                
                self.write_ang_file(file_path, data_to_save)
                
                # Display save information
                info_msg = f"File saved successfully!\n\n"
                info_msg += f"Saved {len(data_to_save['x'])} data points\n"
                if self.applied_operations:
                    info_msg += f"Applied operations: {', '.join(self.applied_operations)}\n"
                if has_changes:
                    info_msg += "\nSaved transformed data:\n"
                    info_msg += f"- X range: {data_to_save['x'].min():.2f} - {data_to_save['x'].max():.2f}\n"
                    info_msg += f"- Y range: {data_to_save['y'].min():.2f} - {data_to_save['y'].max():.2f}\n"
                    # Euler angles in ANG files are in radians, convert to degrees for display
                    info_msg += f"- Phi1 range: {math.degrees(data_to_save['phi1'].min()):.2f}° - {math.degrees(data_to_save['phi1'].max()):.2f}°\n"
                    info_msg += f"- PHI range: {math.degrees(data_to_save['phi'].min()):.2f}° - {math.degrees(data_to_save['phi'].max()):.2f}°\n"
                    info_msg += f"- Phi2 range: {math.degrees(data_to_save['phi2'].min()):.2f}° - {math.degrees(data_to_save['phi2'].max()):.2f}°\n\n"
                    
                    # Display first point comparison (for verification)
                    if len(data_to_save['x']) > 0:
                        info_msg += "First point comparison (verify transformation):\n"
                        if self.original_data is not None:
                            info_msg += f"Original: Phi1={math.degrees(self.original_data['phi1'][0]):.2f}°, "
                            info_msg += f"PHI={math.degrees(self.original_data['phi'][0]):.2f}°, "
                            info_msg += f"Phi2={math.degrees(self.original_data['phi2'][0]):.2f}°\n"
                        info_msg += f"Saved: Phi1={math.degrees(data_to_save['phi1'][0]):.2f}°, "
                        info_msg += f"PHI={math.degrees(data_to_save['phi'][0]):.2f}°, "
                        info_msg += f"Phi2={math.degrees(data_to_save['phi2'][0]):.2f}°"
                else:
                    info_msg += "\nNote: Data unchanged (same as original)"
                
                QMessageBox.information(self, "Success", info_msg)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def write_ang_file(self, file_path, data):
        """写入ANG文件"""
        # 使用ASCII编码保存，确保最大兼容性
        # 使用newline='\n'确保使用Unix风格的换行符（大多数ANG文件使用这种格式）
        with open(file_path, 'w', encoding='ascii', errors='replace', newline='\n') as f:
            # 如果有原始头部信息，优先使用（保留OIM Analysis需要的格式）
            if hasattr(self, 'original_header') and self.original_header:
                # 写入原始头部，但更新数据点数信息
                header_written = False
                for header_line in self.original_header:
                    # 跳过可能包含数据点数的旧注释行，稍后添加新的
                    if 'data point' in header_line.lower() or 'number' in header_line.lower():
                        continue
                    # 写入头部行，确保是ASCII兼容的
                    try:
                        # 尝试将头部行转换为ASCII
                        ascii_line = header_line.encode('ascii', errors='replace').decode('ascii')
                        f.write(ascii_line + '\n')
                        header_written = True
                    except:
                        # 如果转换失败，跳过该行
                        continue
                
                # 如果没有写入任何头部，添加基本头部
                if not header_written:
                    f.write("# ANG file\n")
                    f.write(f"# {len(data['x'])} data points\n")
            else:
                # 如果没有原始头部，写入标准头部
                f.write("# ANG file\n")
                f.write(f"# {len(data['x'])} data points\n")
            
            # 根据原始文件的列数精确匹配保存格式
            # 必须与原始文件格式完全一致
            original_cols = None
            if hasattr(self, 'original_column_count') and self.original_column_count is not None:
                original_cols = self.original_column_count
                print(f"DEBUG: 从original_column_count获取列数: {original_cols}")
            else:
                # 备用：从原始数据推断列数
                if hasattr(self, 'original_data') and self.original_data is not None:
                    # 检查是否有SEM和Fit数据，以及它们的值
                    has_sem = 'sem' in self.original_data and len(self.original_data['sem']) > 0
                    has_fit = 'fit' in self.original_data and len(self.original_data['fit']) > 0
                    
                    if has_sem and has_fit:
                        # 检查SEM是否全为0（如果全为0，可能是9列格式，SEM是默认值）
                        sem_values = np.array(self.original_data['sem'])
                        if np.all(sem_values == 0):
                            # SEM全为0，可能是9列格式（没有SEM列）
                            original_cols = 9
                        else:
                            # SEM有非零值，是10列格式
                            original_cols = 10
                    elif has_fit:
                        # 只有Fit，没有SEM，是9列格式
                        original_cols = 9
                    else:
                        # 没有SEM和Fit，是8列格式
                        original_cols = 8
                    print(f"DEBUG: 从原始数据推断列数: {original_cols}")
            
            if original_cols is None:
                original_cols = 8  # 默认8列
                print(f"DEBUG: 使用默认列数: {original_cols}")
            
            print(f"DEBUG: 最终保存时使用列数: {original_cols}")
            
            # 根据原始列数写入对应的列标题和数据
            # 不写入列标题行（保持与原始文件一致，如果原始文件没有列标题就不写）
            # 但为了兼容性，如果原始头部中有列标题，就保留它
            
            # 写入数据 - 使用TSL .ang标准列顺序
            # 列顺序：phi1, Phi, phi2, x, y, IQ, CI, Phase, SEM, Fit
            for i in range(len(data['x'])):
                # 确保所有值都是有效的
                phi1_val = float(data['phi1'][i])
                phi_val = float(data['phi'][i])
                phi2_val = float(data['phi2'][i])
                x_val = float(data['x'][i])
                y_val = float(data['y'][i])
                iq_val = float(data['iq'][i])
                ci_val = float(data['ci'][i])
                phase_val = int(data['phase'][i])
                
                # 读取SEM和Fit（如果存在）
                sem_val = float(data.get('sem', [0.0] * len(data['x']))[i]) if 'sem' in data and len(data['sem']) > i else 0.0
                fit_val = float(data.get('fit', [100.0] * len(data['x']))[i]) if 'fit' in data and len(data['fit']) > i else 100.0
                
                # 确保Phi2值有效（检查是否为NaN或异常值）
                if np.isnan(phi2_val) or np.isinf(phi2_val):
                    # 如果Phi2无效，尝试使用原始值
                    if hasattr(self, 'original_data') and self.original_data is not None:
                        if i < len(self.original_data['phi2']):
                            phi2_val = float(self.original_data['phi2'][i])
                        else:
                            phi2_val = 0.0
                    else:
                        phi2_val = 0.0
                
                # 调试：检查第一个点的Phi2值
                if i == 0:
                    print(f"DEBUG: 保存第{i}个点 - phi1={phi1_val:.2f}, Phi={phi_val:.2f}, phi2={phi2_val:.2f}, x={x_val:.2f}, y={y_val:.2f}, SEM={sem_val}, Fit={fit_val}")
                
                # 根据原始文件的列数精确匹配格式
                # 原始格式示例：2.408554 3.008948 4.007276     0.000     0.000   73.0  0.290  0     100
                if original_cols == 10:
                    # 10列格式：phi1 Phi phi2 x y IQ CI Phase SEM Fit
                    line = (f"{phi1_val:.6f} {phi_val:.6f} {phi2_val:.6f} "
                           f"{x_val:10.3f} {y_val:10.3f} "
                           f"{iq_val:5.1f} {ci_val:6.3f} "
                           f"{phase_val} {int(sem_val):6d} {int(fit_val):6d}\n")
                elif original_cols == 9:
                    # 9列格式：phi1 Phi phi2 x y IQ CI Phase Fit (没有SEM)
                    line = (f"{phi1_val:.6f} {phi_val:.6f} {phi2_val:.6f} "
                           f"{x_val:10.3f} {y_val:10.3f} "
                           f"{iq_val:5.1f} {ci_val:6.3f} "
                           f"{phase_val} {int(fit_val):6d}\n")
                else:
                    # 8列格式：phi1 Phi phi2 x y IQ CI Phase
                    line = (f"{phi1_val:.6f} {phi_val:.6f} {phi2_val:.6f} "
                           f"{x_val:10.3f} {y_val:10.3f} "
                           f"{iq_val:5.1f} {ci_val:6.3f} "
                           f"{phase_val}\n")
                f.write(line)
    
    def horizontal_mirror(self):
        """左右镜像 (x→-x)，只改变取向，不改变坐标"""
        if self.ang_data is None:
            return
        
        # Transform Euler angles only, do not change X, Y coordinates
        # Euler angles in ANG files are in radians, so use π instead of 180 degrees
        # According to standard formula (horizontal mirror x→-x):
        # φ'_1 = π - φ_1
        # Φ' = Φ
        # φ'_2 = -φ_2
        pi = math.pi
        two_pi = 2 * math.pi
        
        phi1_new = self.ang_data['phi1'].copy()
        phi1_new = (pi - phi1_new) % two_pi
        self.ang_data['phi1'] = phi1_new
        # PHI remains unchanged
        # self.ang_data['phi'] unchanged
        phi2_new = self.ang_data['phi2'].copy()
        phi2_new = (-phi2_new) % two_pi
        self.ang_data['phi2'] = phi2_new
        
        # Track this operation
        if 'horizontal_mirror' not in self.applied_operations:
            self.applied_operations.append('horizontal_mirror')
        
        self.update_preview()
        QMessageBox.information(self, "Complete", "Horizontal mirror applied (orientation only)")
    
    def vertical_mirror(self):
        """上下镜像 (y→-y)，只改变取向，不改变坐标"""
        if self.ang_data is None:
            return
        
        # Transform Euler angles only, do not change X, Y coordinates
        # Euler angles in ANG files are in radians, so use π instead of 180 degrees
        # According to standard formula (vertical mirror y→-y):
        # φ'_1 = -φ_1
        # Φ' = Φ
        # φ'_2 = π - φ_2
        pi = math.pi
        two_pi = 2 * math.pi
        
        phi1_new = self.ang_data['phi1'].copy()
        phi1_new = (-phi1_new) % two_pi
        self.ang_data['phi1'] = phi1_new
        # PHI remains unchanged
        # self.ang_data['phi'] unchanged
        phi2_new = self.ang_data['phi2'].copy()
        phi2_new = (pi - phi2_new) % two_pi
        self.ang_data['phi2'] = phi2_new
        
        # Track this operation
        if 'vertical_mirror' not in self.applied_operations:
            self.applied_operations.append('vertical_mirror')
        
        self.update_preview()
        QMessageBox.information(self, "Complete", "Vertical mirror applied (orientation only)")
    
    def z_axis_rotate(self):
        """Z轴旋转"""
        if self.ang_data is None:
            return
        
        angle_deg = self.rotation_spinbox.value()
        
        if angle_deg == 0:
            return
        
        # Z-axis rotation: directly modify Phi1
        # Euler angles in ANG files are in radians, so convert input degrees to radians
        angle_rad = math.radians(angle_deg)
        two_pi = 2 * math.pi
        # Ensure creating new array instead of view
        self.ang_data['phi1'] = np.mod(self.ang_data['phi1'] + angle_rad, two_pi).copy()
        
        # Track this operation
        operation_name = f'z_rotate_{angle_deg}deg'
        if operation_name not in self.applied_operations:
            self.applied_operations.append(operation_name)
        
        self.update_preview()
        QMessageBox.information(self, "Complete", f"Z-axis rotation {angle_deg}° applied")
    
    def reset_transform(self):
        """Reset transformations"""
        if self.original_data is None:
            return
        
        self.ang_data = {}
        for key in self.original_data:
            self.ang_data[key] = self.original_data[key].copy()
        self.rotation_spinbox.setValue(0)
        self.applied_operations = []  # Clear applied operations
        self.update_preview()
        QMessageBox.information(self, "Complete", "Transformations reset")
    
    def update_preview(self):
        """Update preview"""
        if self.ang_data is None or self.original_data is None:
            return
        
        point_idx = self.preview_spinbox.value()
        
        if point_idx >= len(self.ang_data['x']):
            return
        
        # Clear scenes
        self.before_scene.clear()
        self.after_scene.clear()
        
        # Get original and transformed Euler angles
        orig_phi1 = self.original_data['phi1'][point_idx]
        orig_phi = self.original_data['phi'][point_idx]
        orig_phi2 = self.original_data['phi2'][point_idx]
        
        trans_phi1 = self.ang_data['phi1'][point_idx]
        trans_phi = self.ang_data['phi'][point_idx]
        trans_phi2 = self.ang_data['phi2'][point_idx]
        
        # Draw grain before transformation
        self.draw_grain(self.before_scene, orig_phi1, orig_phi, orig_phi2, 
                       "Before", point_idx, self.before_view)
        
        # Draw grain after transformation
        self.draw_grain(self.after_scene, trans_phi1, trans_phi, trans_phi2, 
                       "After", point_idx, self.after_view)
    
    def euler_to_rotation_matrix(self, phi1, phi, phi2):
        """将欧拉角（Bunge约定）转换为旋转矩阵
        注意：ANG文件中的欧拉角是弧度，不是度数
        """
        # ANG文件中的欧拉角已经是弧度，不需要再转换
        # Bunge约定：Z-X-Z旋转
        cos1 = math.cos(phi1)
        sin1 = math.sin(phi1)
        cos_phi = math.cos(phi)
        sin_phi = math.sin(phi)
        cos2 = math.cos(phi2)
        sin2 = math.sin(phi2)
        
        # 旋转矩阵
        R = np.array([
            [cos1*cos2 - sin1*sin2*cos_phi, -cos1*sin2 - sin1*cos2*cos_phi, sin1*sin_phi],
            [sin1*cos2 + cos1*sin2*cos_phi, -sin1*sin2 + cos1*cos2*cos_phi, -cos1*sin_phi],
            [sin2*sin_phi, cos2*sin_phi, cos_phi]
        ])
        return R
    
    def project_3d_to_2d(self, point_3d, center_x, center_y, scale=50):
        """将3D点投影到2D（等轴测投影）
        标准等轴测投影：
        - X轴（红色）：向右下，稍微向前
        - Y轴（绿色）：向上，稍微向左
        - Z轴（蓝色）：向左下，稍微向上
        """
        x, y, z = point_3d
        # 等轴测投影（标准角度：30度）
        # 根据标准等轴测投影：
        # X轴：向右下（+x方向向右，-z方向向下）
        # Y轴：向上（+y方向向上）
        # Z轴：向左下（-z方向向左，+y方向向上）
        cos_30 = 0.8660254  # cos(30°)
        sin_30 = 0.5        # sin(30°)
        
        # 等轴测投影公式
        # X轴向右下：x向右，z向下
        # Y轴向上：y向上（屏幕Y向下，所以取负）
        # Z轴向左下：z向左，y向上
        x_2d = center_x + scale * (x * cos_30 - z * cos_30)
        y_2d = center_y - scale * (y * cos_30 + (x + z) * sin_30)  # 负号因为屏幕Y向下
        return x_2d, y_2d
    
    def proj_3d_to_2d_simple(self, pt3, cx, cy):
        """简单的3D到2D投影（用于立方体绘制）"""
        return (pt3[0] + cx, -pt3[1] + cy)
    
    def draw_cube(self, scene, phi1, phi, phi2, center_x, center_y, size=4, sigma_axis=None):
        """绘制3D立方体表示晶粒取向（基于原始代码的改进版本）"""
        d = size / 2
        axis_len = size * 0.8
        
        # 1) 构建Bunge ZXZ旋转矩阵
        # ANG文件中的欧拉角已经是弧度，不需要再转换
        phi1_rad, Phi_rad, phi2_rad = phi1, phi, phi2
        c1, s1 = math.cos(phi1_rad), math.sin(phi1_rad)
        c, s = math.cos(Phi_rad), math.sin(Phi_rad)
        c2, s2 = math.cos(phi2_rad), math.sin(phi2_rad)
        
        Rz1 = np.array([[c1, -s1, 0], [s1, c1, 0], [0, 0, 1]])
        Rx = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        Rz2 = np.array([[c2, -s2, 0], [s2, c2, 0], [0, 0, 1]])
        Rm = Rz1 @ Rx @ Rz2
        
        # 辅助函数：投影3D点到2D
        def proj(pt3):
            return (pt3[0] + center_x, -pt3[1] + center_y)
        
        # 2) 绘制全局坐标系（样品坐标系，固定）
        # X轴（红色，实线，向右）
        x_end = proj(np.array([axis_len, 0, 0]))
        x_line = QGraphicsLineItem(center_x, center_y, x_end[0], x_end[1])
        x_line.setPen(QPen(Qt.red, 2))
        scene.addItem(x_line)
        x_label = scene.addText("X", QFont("Arial", 7))
        x_label.setPos(x_end[0] + 3, x_end[1])
        x_label.setDefaultTextColor(Qt.red)
        
        # Y轴（蓝色，虚线，向上）
        y_end = proj(np.array([0, axis_len, 0]))
        y_line = QGraphicsLineItem(center_x, center_y, y_end[0], y_end[1])
        y_pen = QPen(Qt.blue, 2)
        y_pen.setStyle(Qt.PenStyle.DashLine)
        y_line.setPen(y_pen)
        scene.addItem(y_line)
        y_label = scene.addText("Y", QFont("Arial", 7))
        y_label.setPos(y_end[0], y_end[1] - 10)
        y_label.setDefaultTextColor(Qt.blue)
        
        # Z轴（绿色点，向前）
        rdot = 4
        z_circle = QGraphicsEllipseItem(center_x - rdot, center_y - rdot, rdot * 2, rdot * 2)
        z_circle.setBrush(QBrush(Qt.green))
        z_circle.setPen(QPen(Qt.green, 1))
        scene.addItem(z_circle)
        z_label = scene.addText("Z", QFont("Arial", 7))
        z_label.setPos(center_x + rdot + 3, center_y + rdot + 3)
        z_label.setDefaultTextColor(Qt.green)
        
        # 3) 图例（右下角）
        legend = [
            ('[100]', QColor(255, 0, 255)),  # magenta
            ('[010]', QColor(255, 165, 0)),  # orange
            ('[001]', QColor(0, 128, 128)),  # teal
        ]
        # 获取场景尺寸以计算右下角位置
        scene_rect = scene.sceneRect()
        scene_width = scene_rect.width()
        scene_height = scene_rect.height()
        
        line_len = 20
        legend_width = line_len + 50  # 线条长度 + 文字宽度
        legend_height = len(legend) * 20  # 每个图例项20像素高
        
        # 右下角位置：从右边和底部留出一些边距
        margin = 10
        lx = scene_width - legend_width - margin
        ly_start = scene_height - legend_height - margin
        
        for i, (label, color) in enumerate(legend):
            y_pos = ly_start + i * 20
            legend_line = QGraphicsLineItem(lx, y_pos, lx + line_len, y_pos)
            legend_line.setPen(QPen(color, 3))
            scene.addItem(legend_line)
            legend_text = scene.addText(label, QFont("Arial", 8))
            legend_text.setPos(lx + line_len + 5, y_pos - 6)
            legend_text.setDefaultTextColor(color)
        
        # 4) 计算旋转后的立方体顶点并投影
        verts = np.array([
            [-d, -d, -d], [-d, -d, d], [-d, d, -d], [-d, d, d],
            [d, -d, -d], [d, -d, d], [d, d, -d], [d, d, d]
        ])
        rot_verts = verts @ Rm.T
        proj2 = [proj(p) for p in rot_verts]
        
        # 5) 定义面和法向量（用于判断可见性）
        faces = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1],
                 [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
        normals = [np.array([-1, 0, 0]), np.array([1, 0, 0]),
                   np.array([0, -1, 0]), np.array([0, 1, 0]),
                   np.array([0, 0, -1]), np.array([0, 0, 1])]
        face_vis = [(Rm @ n)[2] > 0 for n in normals]
        
        # 6) 按方向分组绘制边
        edges = {
            '[100]': [(0, 4), (1, 5), (2, 6), (3, 7)],  # 沿X方向的边
            '[010]': [(0, 2), (1, 3), (4, 6), (5, 7)],  # 沿Y方向的边
            '[001]': [(0, 1), (2, 3), (4, 5), (6, 7)],  # 沿Z方向的边
        }
        colors = {
            '[100]': QColor(255, 0, 255),  # magenta
            '[010]': QColor(255, 165, 0),  # orange
            '[001]': QColor(0, 128, 128),  # teal
        }
        
        for label, eds in edges.items():
            col = colors[label]
            for i, j in eds:
                # 检查边是否在前面（可见）
                adj = [fi for fi, face in enumerate(faces) if i in face and j in face]
                front = any(face_vis[fi] for fi in adj)
                
                x1, y1 = proj2[i]
                x2, y2 = proj2[j]
                
                line = QGraphicsLineItem(x1, y1, x2, y2)
                if front:
                    line.setPen(QPen(col, 2))
                else:
                    pen = QPen(col, 1)
                    pen.setStyle(Qt.PenStyle.DashLine)
                    pen.setDashPattern([4, 2])
                    line.setPen(pen)
                scene.addItem(line)
        
        # 7) 可选：绘制Sigma旋转轴（如果提供）
        if sigma_axis is not None:
            axis_norm = sigma_axis / np.linalg.norm(sigma_axis)
            axis_len_draw = size * 1.2
            start = np.array([0, 0, 0])
            end = axis_len_draw * axis_norm
            start_rot = start @ Rm.T
            end_rot = end @ Rm.T
            x1, y1 = proj(start_rot)
            x2, y2 = proj(end_rot)
            sigma_line = QGraphicsLineItem(x1, y1, x2, y2)
            sigma_line.setPen(QPen(Qt.black, 3))
            scene.addItem(sigma_line)
            sigma_label = scene.addText("Σ axis", QFont("Arial", 7))
            sigma_label.setPos(x2 + 5, y2 + 5)
            sigma_label.setDefaultTextColor(Qt.black)
    
    def draw_grain(self, scene, phi1, phi, phi2, title, point_idx, view=None):
        """绘制晶粒表示，显示3D立方体"""
        # 获取视图大小，如果没有提供则使用默认值
        if view is not None:
            view_size = view.size()
            scene_width = max(300, view_size.width() - 20)
            scene_height = max(300, view_size.height() - 20)
        else:
            scene_width = 300
            scene_height = 400
        
        # 设置场景大小
        scene.setSceneRect(0, 0, scene_width, scene_height)
        
        # 添加标题
        title_text = scene.addText(title, QFont("Arial", 12, QFont.Bold))
        title_text.setPos(10, 10)
        
        # Display Euler angle information
        info_text = f"Point Index: {point_idx}\n"
        # Euler angles in ANG files are in radians, convert to degrees for display
        info_text += f"Phi1: {math.degrees(phi1):.2f}°\n"
        info_text += f"PHI: {math.degrees(phi):.2f}°\n"
        info_text += f"Phi2: {math.degrees(phi2):.2f}°"
        
        info_label = scene.addText(info_text, QFont("Arial", 10))
        info_label.setPos(10, 35)
        
        # 计算立方体位置和大小，使其适应窗口
        # 预留空间给标题和信息（约100像素）
        available_height = scene_height - 100
        available_width = scene_width - 20
        
        # Cube size: take minimum of available space, make it 2x larger
        cube_size = min(available_width, available_height) * 0.3  # 2x larger (was 0.15)
        cube_size = max(30, min(cube_size, 80))  # Limit between 30-80 (2x of previous 15-40)
        
        # 立方体中心位置
        cube_center_x = scene_width / 2
        cube_center_y = (scene_height + 50) / 2  # 稍微偏下，给标题留空间
        
        # 绘制3D立方体
        self.draw_cube(scene, phi1, phi, phi2, cube_center_x, cube_center_y, size=cube_size)
        
        # 添加坐标轴标签（根据立方体大小调整位置，更紧凑）
        label_offset = cube_size * 0.7
        label_x = scene.addText("X", QFont("Arial", 7, QFont.Bold))
        label_x.setPos(cube_center_x + label_offset, cube_center_y - 3)
        label_x.setDefaultTextColor(Qt.red)
        
        label_y = scene.addText("Y", QFont("Arial", 7, QFont.Bold))
        label_y.setPos(cube_center_x - 3, cube_center_y - label_offset)
        label_y.setDefaultTextColor(Qt.blue)  # Y轴是蓝色
        
        label_z = scene.addText("Z", QFont("Arial", 7, QFont.Bold))
        label_z.setPos(cube_center_x + 3, cube_center_y + label_offset)
        label_z.setDefaultTextColor(QColor(255, 20, 147))  # Z轴是粉色
        
        # 如果提供了视图，自动适应场景
        if view is not None:
            # 延迟执行fitInView，确保视图大小已更新
            from PyQt5.QtCore import QTimer
            def fit_view():
                if scene.sceneRect().isValid():
                    view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            QTimer.singleShot(50, fit_view)


def main():
    app = QApplication(sys.argv)
    window = AngProcessor()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

