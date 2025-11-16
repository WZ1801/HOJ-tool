from lib import interaction
from lib.api import HOJ as HOJapi
import os

def main(HOJ: HOJapi):
    """排名主函数"""
    os.system('cls')
    match interaction.get_case(["OI", "ACM", "exit"], '排名模式'):
        case "OI":
            os.system('cls')
            interaction.show_message('正在获取所有排名数据，请稍候...', 'info')
            rank = HOJ.get_rank(get_all=True)
            if rank:
                interaction.show_rank(rank, mode='oi')
            else:
                interaction.show_message('获取排名失败', 'error')
        case "ACM":
            os.system('cls')
            interaction.show_message('正在获取所有排名数据，请稍候...', 'info')
            rank = HOJ.get_rank(mode='acm', get_all=True)
            if rank:
                interaction.show_rank(rank, mode='acm')
            else:
                interaction.show_message('获取排名失败', 'error')