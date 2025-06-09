import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import os
import re

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False     # 用来正常显示负号

def read_txt_file(filepath):
    """读取转换后的txt格式光谱数据"""
    try:
        # 读取txt文件，使用制表符分隔
        data = pd.read_csv(filepath, sep='\t')
        # 获取文件名（不含扩展名）作为反射率列名
        reflectance_col = data.columns[1]
        # 提取数据
        wavelengths = data['Wavelength'].values
        reflectance = data[reflectance_col].values
        return wavelengths, reflectance
    except Exception as e:
        print(f"读取文件出错: {str(e)}")
        return None, None

# 修改文件路径设置
base_path = r"G:\lin\G2024"



# 获取所有txt文件并排序
txt_files = []
for file in os.listdir(base_path):
    if file.endswith('.txt'):
        # 提取文件名中的所有数字
        numbers = re.findall(r'\d+', file)
        if numbers:
            # 将所有数字连接成一个字符串
            number = int(''.join(numbers))
            txt_files.append((number, file))

# 按数字排序
txt_files.sort(key=lambda x: x[0])

# 创建结果DataFrame
result_df = None
wavelengths = None

# 每10个文件为一组处理
for i in range(0, len(txt_files), 10):
    try:
        batch_files = txt_files[i:i+10]

        # 读取该批次的文件
        spectra_data = {}
        for number, filename in batch_files:
            filepath = os.path.join(base_path, filename)
            try:
                wave, spectrum = read_txt_file(filepath)
                if wave is not None:
                    if wavelengths is None:
                        wavelengths = wave
                    spectra_data[number] = spectrum
            except Exception as e:
                print(f"无法读取文件 {filename}: {str(e)}")

        if not spectra_data:
            continue

        # 绘制该批次的光谱曲线
        fig, ax = plt.subplots(figsize=(12, 6))
        lines = []
        for idx, (number, spectrum) in enumerate(spectra_data.items(), 1):
            line, = ax.plot(wavelengths, spectrum, label=f'曲线{idx}')
            lines.append(line)

        ax.set_xlabel('波长 (nm)')
        ax.set_ylabel('反射率')
        ax.set_title(f'光谱曲线 (批次 {i//10 + 1})')
        ax.grid(True)
        ax.set_ylim(0, 1)
        ax.set_xlim(300, 1100)

        # 添加交互式标签
        cursor = mplcursors.cursor(lines, hover=True)
        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set_text(sel.artist.get_label())

        plt.show()

        # 手动删除异常值
        print(f"\n当前批次曲线编号 1-{len(spectra_data)}")
        to_remove = input("请输入需要删除的编号（多个编号用点号分隔，如 1.2.3，直接回车表示不删除）: ").split('.')
        to_remove = [list(spectra_data.keys())[int(x)-1] for x in to_remove if x.isdigit() and 1 <= int(x) <= len(spectra_data)]

        # 删除指定的文件
        for number in to_remove:
            if number in spectra_data:
                del spectra_data[number]

        # 计算平均值
        if spectra_data:
            mean_spectrum = np.mean([spectrum for spectrum in spectra_data.values()], axis=0)

            # 将结果添加到DataFrame
            if result_df is None:
                result_df = pd.DataFrame({'波长': wavelengths})
            result_df[f'反射率_批次{i//10 + 1}'] = mean_spectrum
            print(f"\n批次 {i//10 + 1} 均值计算完成")

    except Exception as e:
        print(f"\n批次 {i//10 + 1} 处理出错: {str(e)}")
        print("继续处理下一批次...")
        continue

# 保存汇总结果
if result_df is not None:
    output_dir = base_path
    output_path = os.path.join(output_dir, "光谱均值汇总.csv")
    result_df.to_csv(output_path, index=False)
    print(f"\n汇总数据已保存至: {output_path}")
else:
    print("没有有效的数据可供处理")
