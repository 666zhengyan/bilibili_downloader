import subprocess,os

def merge_m4s_to_mp4(input_files, output_file, GPU, save_path=r'D:'):
    # 通过FFmpeg将两个M4S文件合并成一个普通播放器可播放的MP4文件
    command = ['ffmpeg']
    for input_file in input_files:
        command.extend(['-i', input_file])
    command.extend(['-codec', 'copy', f'{save_path}/{output_file}'])
    subprocess.run(command)
    # # 构造 ffmpeg 命令,尝试转码
    # print('开始转码')
    # if GPU == True:
    #     command = ['ffmpeg', '-hwaccel_output_format', 'cuda', '-i', f'temp{output_file}', '-c:v', 'h264_nvenc', '-c:a', 'aac',
    #                f'{save_path}/{output_file}']
    # else:
    #     command = ['ffmpeg', '-i', f'temp{output_file}', '-c:v', 'libx264', '-c:a', 'aac', f'{save_path}/{output_file}']
    # # 执行命令
    # subprocess.run(command)
    # for input_file in input_files:
    #     os.remove(input_file)
    # os.remove(f'temp{output_file}')

def find_files(source_folder, target_file):
    """
    该函数的作用是查找某一文件夹下面符合描述的文件的路径，返回一个列表
    符合描述的意思是文件名相同或者后缀相同
    :param source_folder:源文件夹路径
    :param target_file:目标文件的名称
    :return:一个列表，装着的是路径
    """
    path_list=[]
    # 递归遍历源文件夹
    """
     os.walk 函数递归遍历指定的源文件夹 source_folder。
     os.walk 返回一个生成器，每次迭代会返回一个三元组 (root, dirs, files)，
     其中 root 是当前目录的路径，dirs 是当前目录下的子目录列表，files 是当前目录下的文件列表。
    """
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            #检查文件是否以 target_file 结尾或者文件的基本名称（不包含路径）是否等于 target_file。
            if file.endswith(target_file) or os.path.basename(file)==target_file:
                #使用 os.path.join 将当前文件的路径拼接到根路径上，得到完整的文件路径。
                source_path = os.path.join(root, file)
                path_list.append(source_path)

    return path_list

def remove_files(source_folder, target_file):
    """
    这个函数的作用是删除某文件夹下面所有符合描述的文件
    :param source_folder:
    :param target_file:
    :return:
    """
    path_list=find_files(source_folder, target_file)
    for i in path_list:
        os.remove(i)


def m4s_to_ts(inputlist):
    # 列表中包含所有的.m4s视频片段
    m4s_segments = inputlist
    print(len(m4s_segments))
    ts_segments = []
    # 转换每个.m4s片段到.ts格式
    with open('tsfilelist.txt','w') as f:
        for segment in m4s_segments:
            print(segment.name)
            ts_segment = segment.name.replace('.m4s', '.ts')
            ts_segments.append(ts_segment)
            subprocess.run([
                'ffmpeg',
                '-i', segment.name,
                '-c', 'copy',
                '-bsf:v', 'h264_mp4toannexb',
                '-f', 'mpegts',
                ts_segment
            ])
            f.write(f"file '{ts_segment}'\n")
    #尝试将ts全部合并为mp4
    ffmpeg_command = f'ffmpeg -f concat -safe 0 -i "tsfilelist.txt" -c copy "ouput.mp4"'
    subprocess.run(ffmpeg_command, check=True, shell=True)

if __name__=="__main__":
    merge_m4s_to_mp4(input_files=['video-辉夜大小姐想让我告白_-究极浪漫-_第5话_藤原千花想唱出范___早坂爱有话想说___四条真妃想依靠.m4s','audio-辉夜大小姐想让我告白_-究极浪漫-_第5话_藤原千花想唱出范___早坂爱有话想说___四条真妃想依靠.m4s'],output_file="测试.mp4",GPU=True)
