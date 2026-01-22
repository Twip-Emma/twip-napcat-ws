from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
import pandas as pd
from datetime import datetime
import tempfile
import os
import time
from typing import List, Dict, Any
import base64
import aiofiles

__plugin_meta__ = PluginMetadata(
    name="群成员导出",
    description="导出群成员数据为Excel文件",
    usage="群成员导出 [群号] - 导出群成员数据",
    type="application",
    supported_adapters={"~onebot.v11"},
)

export_members = on_command(
    "群成员导出",
    aliases={"导出群成员"},
    priority=10,
    block=True
)


def convert_timestamp(timestamp: int) -> str:
    """转换时间戳为可读格式"""
    if timestamp == 0:
        return ""
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)


def convert_role(role: str) -> str:
    """转换角色为中文"""
    role_map = {"owner": "群主", "admin": "管理员", "member": "成员"}
    return role_map.get(role, role)


def convert_sex(sex: str) -> str:
    """转换性别为中文"""
    sex_map = {"male": "男", "female": "女", "unknown": "未知"}
    return sex_map.get(sex, sex)


def process_member_data(member: Dict[str, Any]) -> Dict[str, Any]:
    """处理单个成员数据"""
    return {
        "用户ID": member.get("user_id", ""),
        "QQ昵称": member.get("nickname", ""),
        "群名片": member.get("card", "") or member.get("nickname", ""),
        "性别": convert_sex(member.get("sex", "unknown")),
        "年龄": member.get("age", 0),
        "地区": member.get("area", ""),
        "QQ等级": member.get("qq_level", 0),
        "群等级": member.get("level", ""),
        "入群时间": convert_timestamp(member.get("join_time", 0)),
        "最后发言时间": convert_timestamp(member.get("last_sent_time", 0)),
        "角色": convert_role(member.get("role", "member")),
        "专属头衔": member.get("title", ""),
        "禁言状态": "是" if member.get("shut_up_timestamp", 0) > time.time() else "否",
        "是否机器人": "是" if member.get("is_robot", False) else "否",
    }


def create_excel_file(members_data: List[Dict[str, Any]], group_id: int) -> str:
    """创建Excel文件并返回文件路径"""
    print(f"开始处理{len(members_data)}条成员数据")

    # 处理数据
    processed_data = []
    for member in members_data:
        processed_data.append(process_member_data(member))

    # 创建DataFrame
    df = pd.DataFrame(processed_data)

    # 设置列顺序
    column_order = [
        "用户ID", "QQ昵称", "群名片", "性别", "年龄", "地区",
        "QQ等级", "群等级", "入群时间", "最后发言时间", "角色",
        "专属头衔", "禁言状态", "是否机器人"
    ]
    df = df[column_order]

    # 创建临时文件
    temp_dir = tempfile.mkdtemp(prefix="qqgroup_export_")
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"群成员_{group_id}_{current_time}.xlsx"
    filepath = os.path.join(temp_dir, filename)

    # 保存为Excel
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='群成员')

        # 调整列宽
        worksheet = writer.sheets['群成员']
        column_widths = {
            "A": 12, "B": 15, "C": 15, "D": 8, "E": 8, "F": 15,
            "G": 10, "H": 10, "I": 18, "J": 18, "K": 10,
            "L": 15, "M": 10, "N": 10
        }
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

    print(f"Excel文件已生成: {filepath}")

    return filepath


@export_members.handle()
async def handle_export(bot: Bot, event: GroupMessageEvent, args=CommandArg()):
    # 获取群号
    group_id = event.group_id
    arg_text = args.extract_plain_text().strip()

    # 如果提供了参数，检查权限
    if arg_text:
        if not await SUPERUSER(bot, event):
            await export_members.finish("只有超级用户才能导出其他群的数据")
        try:
            group_id = int(arg_text)
        except ValueError:
            await export_members.finish("请提供有效的群号")

    print(f"开始导出群{group_id}的成员数据")

    # 获取群成员列表
    try:
        member_list = await bot.get_group_member_list(group_id=group_id)
        if not member_list:
            await export_members.finish("获取群成员数据失败或群成员为空")
        print(f"成功获取{len(member_list)}名成员数据")
    except Exception as e:
        print(f"获取群成员数据失败: {e}")
        await export_members.finish("获取群成员数据失败")

    # 创建Excel文件
    try:
        excel_path = create_excel_file(member_list, group_id)
        file_size = os.path.getsize(excel_path)
        filename = os.path.basename(excel_path)
        print(f"Excel文件生成完成，大小: {file_size}字节")
    except Exception as e:
        print(f"生成Excel文件失败: {e}")
        await export_members.finish("生成Excel文件失败")

    # 使用 base64 方式上传文件
    print(f"开始以base64方式上传文件到群{event.group_id}: {excel_path}")

    try:
        # 读取文件内容并转换为base64
        async with aiofiles.open(excel_path, 'rb') as f:
            file_content = await f.read()
        
        # 将文件内容编码为base64
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        print(f"文件base64编码完成，长度: {len(file_base64)}")
        
        # 方法1: 尝试使用base64://格式
        try:
            await bot.call_api(
                "upload_group_file",
                group_id=event.group_id,
                file=f"base64://{file_base64}",  # base64格式
                name=filename
            )
            print(f"base64格式上传成功: {filename}")
        except Exception as e:
            print(f"base64格式上传失败，尝试其他方法: {e}")
            
            # 方法2: 直接传递base64字符串（不带前缀）
            try:
                await bot.call_api(
                    "upload_group_file",
                    group_id=event.group_id,
                    file=file_base64,  # 直接传递base64字符串
                    name=filename
                )
                print(f"直接base64上传成功: {filename}")
            except Exception as e2:
                print(f"所有base64方式都失败: {e2}")
                
                # 方法3: 作为bytes传递（如果API支持）
                try:
                    await bot.call_api(
                        "upload_group_file",
                        group_id=event.group_id,
                        file=file_content,  # 直接传递bytes
                        name=filename
                    )
                    print(f"bytes方式上传成功: {filename}")
                except Exception as e3:
                    print(f"所有方式都失败: {e3}")
                    
                    # 最后尝试原始的文件路径方式（带str转换）
                    try:
                        await bot.call_api(
                            "upload_group_file",
                            group_id=event.group_id,
                            file=str(excel_path),  # 转换为字符串
                            name=filename
                        )
                        print(f"文件路径方式上传成功: {filename}")
                    except Exception as e4:
                        print(f"所有上传方式都失败: {e4}")
                        raise e4
        
        # 上传成功后的处理
        print(f"文件上传成功: {filename}")
        
        # 清理临时文件
        try:
            os.remove(excel_path)
            os.rmdir(os.path.dirname(excel_path))
            print("临时文件已清理")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {e}")
        
        # 返回成功消息
        await export_members.finish(f"✅ 群成员导出完成，文件已上传到群文件：{filename}")
        
    except Exception as e:
        print(f"文件上传失败: {e}")
        
        # 清理临时文件
        os.remove(excel_path)
        os.rmdir(os.path.dirname(excel_path))
