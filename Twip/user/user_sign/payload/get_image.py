from PIL import Image, ImageDraw, ImageFont
import random
from .db import sql_dml, sql_dql
import datetime
import uuid
from pathlib import Path
ABSOLUTE_PATH: str = Path(__file__).absolute().parents[0]
TTF = Path(ABSOLUTE_PATH) / "zh-cn.ttf"


# 绘制背景 - 修改为菱形分布
def draw_circles(image):
    draw = ImageDraw.Draw(image)

    # 定义圆的半径和圆心之间的距离（保持原来的100）
    radius = 5
    distance = 100  # 保持原来的100像素间距

    # 图片尺寸 - 增大以适应菱形分布
    width, height = 1600, 1600  # 增大尺寸
    
    # 定义菱形分布的参数
    # 总行数：15行（1,3,5,7,9,11,13,15,13,11,9,7,5,3,1）
    # 中心行是第8行（索引7），中心列是第8列（索引7）
    
    center_row_index = 7  # 中心行索引
    center_col_index = 7  # 中心列索引
    
    # 中心点的坐标（第7行第7列）
    center_x = 100 + center_col_index * distance
    center_y = 100 + center_row_index * distance
    
    # 生成菱形分布的圆点坐标
    valid_positions = set()  # 用于记录有效的圆点位置
    position_matrix = {}     # 用于快速查找位置
    
    for row in range(15):  # 总共15行
        # 计算当前行距离中心行的距离
        row_distance_from_center = abs(row - center_row_index)
        
        # 计算当前行的圆点数量
        dots_in_row = 15 - 2 * row_distance_from_center
        
        # 计算当前行的y坐标
        current_y = center_y - (center_row_index - row) * distance
        
        # 计算当前行的起始列索引
        start_col_index = center_col_index - (dots_in_row // 2)
        
        # 绘制当前行的所有圆点
        for col_offset in range(dots_in_row):
            col_index = start_col_index + col_offset
            current_x = center_x + (col_index - center_col_index) * distance
            
            # 记录位置
            pos = (current_x, current_y)
            valid_positions.add(pos)
            position_matrix[(row, col_index)] = pos
            
            # 绘制白色小圆点
            draw.ellipse(
                [
                    (current_x - radius, current_y - radius),
                    (current_x + radius, current_y + radius)
                ],
                fill=(255, 255, 255)
            )
    
    return image, valid_positions, position_matrix, center_x, center_y, distance, center_row_index, center_col_index


# 写字
async def draw_bg():
    # 创建一个黑色背景的图片（增大尺寸）
    width, height = 1600, 1600  # 增大尺寸
    background_color = (0, 0, 0)
    image = Image.new("RGB", (width, height), background_color)

    # 调用绘制圆点的函数，并获取有效位置
    image_with_circles, valid_positions, position_matrix, center_x, center_y, distance, center_row_index, center_col_index = draw_circles(image)
    draw = ImageDraw.Draw(image_with_circles)

    # 定义字体和文字
    font_path = TTF  # 替换为你的字体文件路径
    font_size = 20
    font = ImageFont.truetype(font_path, font_size)

    # 定义文字列表
    characters = ["青", "白", "朱", "玄", "南", "参", "北", "玉"]

    # 定义字往右下角偏移的值
    drift = 5

    # 记录已绘制文字的坐标
    drawn_coordinates = set()

    # 定义中心点（第7行第7列）
    center_point = (center_x + drift, center_y + drift)
    
    # 获取菱形的四个顶点坐标
    # 1. 上顶点：第0行唯一的点
    # 2. 右顶点：第7行最右边的点（第14列）
    # 3. 下顶点：第14行唯一的点  
    # 4. 左顶点：第7行最左边的点（第0列）
    
    corner_points = []
    
    # 上顶点 - 第0行唯一的点
    top_row = 0
    for col in range(15):
        if (top_row, col) in position_matrix:
            corner_points.append(position_matrix[(top_row, col)])
            break
    
    # 右顶点 - 第7行最右边的点（第14列）
    center_row = 7
    right_col = 14
    if (center_row, right_col) in position_matrix:
        corner_points.append(position_matrix[(center_row, right_col)])
    
    # 下顶点 - 第14行唯一的点
    bottom_row = 14
    for col in range(15):
        if (bottom_row, col) in position_matrix:
            corner_points.append(position_matrix[(bottom_row, col)])
            break
    
    # 左顶点 - 第7行最左边的点（第0列）
    left_col = 0
    if (center_row, left_col) in position_matrix:
        corner_points.append(position_matrix[(center_row, left_col)])
    
    # 如果找不到某个顶点，使用默认位置
    while len(corner_points) < 4:
        # 补充缺失的顶点
        if len(corner_points) == 0:
            corner_points.append((center_x, center_y - 7 * distance))  # 上
        if len(corner_points) == 1:
            corner_points.append((center_x + 7 * distance, center_y))  # 右
        if len(corner_points) == 2:
            corner_points.append((center_x, center_y + 7 * distance))  # 下
        if len(corner_points) == 3:
            corner_points.append((center_x - 7 * distance, center_y))  # 左

    # 绘制固定文字
    # 中心点：空（红色）
    draw.text(center_point, "空", font=font, fill=(255, 0, 0))
    drawn_coordinates.add(center_point)
    
    # 四个顶点：吉、平、诡、厄（黄色）
    corner_labels = ["吉", "平", "诡", "厄"]
    for i in range(4):
        point = (corner_points[i][0] + drift, corner_points[i][1] + drift)
        draw.text(point, corner_labels[i], font=font, fill=(255, 255, 0))
        drawn_coordinates.add(point)


    # 判断当日是否生成了文字坐标
    character_data = await sql_dql(
        "select sign from user_sign where user_id=? and time=?",
        (
            "系统",
            datetime.datetime.now().strftime("%Y-%m-%d")
        )
    )
    if character_data != []:
        point_list = parse_coordinates_string(character_data[0][0])
        for index in range(len(characters)):
            draw.text((point_list[index][0], point_list[index][1]), characters[index], font=font, fill=(255, 255, 255))
    else:
        add_list = []
        # 从菱形范围内的有效位置中随机选择8个点（排除已使用的位置）
        # 首先获取菱形内的所有有效位置（排除中心点和四个顶点）
        available_positions = list(valid_positions - drawn_coordinates)
        
        # 确保至少8个可用位置
        if len(available_positions) < 8:
            # 如果位置不够，重新生成菱形内所有可能的位置
            all_rhombus_positions = set()
            for row in range(15):
                row_distance_from_center = abs(row - center_row_index)
                dots_in_row = 15 - 2 * row_distance_from_center
                current_y = center_y - (center_row_index - row) * distance
                start_col_index = center_col_index - (dots_in_row // 2)
                
                for col_offset in range(dots_in_row):
                    col_index = start_col_index + col_offset
                    current_x = center_x + (col_index - center_col_index) * distance
                    all_rhombus_positions.add((current_x, current_y))
            
            # 从所有菱形位置中排除已使用的位置
            available_positions = list(all_rhombus_positions - drawn_coordinates)
        
        random.shuffle(available_positions)
        
        for character in characters:
            while available_positions:
                pos = available_positions.pop()
                pos_with_drift = (pos[0] + drift, pos[1] + drift)
                if pos_with_drift not in drawn_coordinates:
                    drawn_coordinates.add(pos_with_drift)
                    add_list.append(pos_with_drift)
                    draw.text(pos_with_drift, character, font=font, fill=(255, 255, 255))
                    break
        
        await sql_dml(
            "insert into user_sign (id, user_id, time, sign)values(?,?,?,?)",
            (
                str(uuid.uuid4()),
                "系统",
                datetime.datetime.now().strftime("%Y-%m-%d"),
                str(add_list)
            )
        )
    
    return image_with_circles, valid_positions, position_matrix, center_x, center_y, distance, center_row_index, center_col_index


# 在两个点之间画线段
def draw_line_between_points(image, point1, point2):
    draw = ImageDraw.Draw(image)

    # 定义直线颜色和宽度
    line_color = (255, 255, 255)
    line_width = 6

    # 绘制直线
    draw.line([point1, point2], fill=line_color, width=line_width)
    return image


# 随机生成路径 - 只在有效圆点位置之间移动
def generate_random_circle_coordinates():
    # 生成菱形分布的有效位置
    distance = 100
    center_row_index = 7
    center_col_index = 7
    center_x = 100 + center_col_index * distance
    center_y = 100 + center_row_index * distance
    
    valid_positions = set()
    position_matrix = {}
    
    for row in range(15):
        row_distance_from_center = abs(row - center_row_index)
        dots_in_row = 15 - 2 * row_distance_from_center
        current_y = center_y - (center_row_index - row) * distance
        start_col_index = center_col_index - (dots_in_row // 2)
        
        for col_offset in range(dots_in_row):
            col_index = start_col_index + col_offset
            current_x = center_x + (col_index - center_col_index) * distance
            pos = (current_x, current_y)
            valid_positions.add(pos)
            position_matrix[(row, col_index)] = pos
    
    # 定义相邻方向（8个方向，每个方向100像素）
    directions = [
        (-distance, -distance), (0, -distance), (distance, -distance),
        (-distance, 0), (distance, 0),
        (-distance, distance), (0, distance), (distance, distance)
    ]
    
    # 从中心点开始（第7行第7列）
    initial_point = (center_x, center_y)
    circle_coordinates = [initial_point]
    used_coordinates = set([initial_point])
    
    # 为每个位置找到有效的相邻位置
    position_neighbors = {}
    for pos in valid_positions:
        neighbors = []
        for direction in directions:
            neighbor_pos = (pos[0] + direction[0], pos[1] + direction[1])
            if neighbor_pos in valid_positions:
                neighbors.append(neighbor_pos)
        position_neighbors[pos] = neighbors
    
    for _ in range(30):
        current_pos = circle_coordinates[-1]
        possible_next = []
        
        # 获取当前点的所有有效邻居
        if current_pos in position_neighbors:
            neighbors = position_neighbors[current_pos]
            possible_next = [pos for pos in neighbors if pos not in used_coordinates]
        
        if possible_next:
            # 随机选择一个有效邻居
            next_pos = random.choice(possible_next)
            circle_coordinates.append(next_pos)
            used_coordinates.add(next_pos)
        else:
            # 如果没有可用邻居，回到中心点
            circle_coordinates.append(initial_point)
            used_coordinates.add(initial_point)
    
    return circle_coordinates


# 写字
def write_char(char_name, bg):
    bg_size = bg.size
    font = ImageFont.truetype(TTF, 50)
    draw = ImageDraw.Draw(bg)
    
    # 直接使用textlength获取宽度（Pillow 8.0.0+）
    text_width = font.getlength(char_name)
    
    # 写字 - 在底部居中位置
    draw.text((int((bg_size[0]-text_width)/2), bg_size[1] - 75),
              char_name, fill="#ffffffff", font=font)
    return bg


# 数据转换-str转list
def parse_coordinates_string(coordinates_string):
    # 移除首尾的方括号，并按逗号分隔字符串
    coordinates_list = coordinates_string.strip('[]').replace("(","").replace(")","").split(",")

    # 提取每个坐标点的 x 和 y，并转换为整数
    parsed_coordinates = [(int(coordinates_list[i]), int(coordinates_list[i + 1])) for i in range(0, len(coordinates_list), 2)]

    return parsed_coordinates


# 获取签到图
async def get_sign_image(user_id: str, user_name: str, random_circle_coordinates: list = None):
    if not random_circle_coordinates:
        random_circle_coordinates = generate_random_circle_coordinates()
        await sql_dml(
            "insert into user_sign (id, user_id, time, sign)values(?,?,?,?)",
            (
                str(uuid.uuid4()),
                user_id,
                datetime.datetime.now().strftime("%Y-%m-%d"),
                str(random_circle_coordinates)
            )
        )
    
    # 获取背景和有效位置
    bg, valid_positions, position_matrix, center_x, center_y, distance, center_row_index, center_col_index = await draw_bg()
    
    # 确保所有坐标都在有效位置中（带偏移）
    drift = 5
    adjusted_coordinates = []
    for coord in random_circle_coordinates:
        # 如果有偏移需求，可以在这里添加
        adjusted_coord = (coord[0] + drift, coord[1] + drift)
        # 确保坐标在有效范围内
        if coord not in valid_positions:
            # 找到最近的有效点
            closest_point = min(valid_positions, key=lambda p: 
                               (p[0]-coord[0])**2 + (p[1]-coord[1])**2)
            adjusted_coord = (closest_point[0] + drift, closest_point[1] + drift)
        adjusted_coordinates.append(adjusted_coord)
    
    # 绘制线条
    for index in range(len(adjusted_coordinates) - 1):
        if index != 0 and adjusted_coordinates[index + 1] == (center_x + drift, center_y + drift):
            continue
        bg = draw_line_between_points(bg, adjusted_coordinates[index], adjusted_coordinates[index + 1])
    
    # 最后在bg上居中位置且靠底部的位置写字
    bg = write_char(user_name, bg)
    save = Path(ABSOLUTE_PATH) / "cache" / f"{user_id}.jpg"
    bg.save(save)
    return save