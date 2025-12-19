from lib import interaction
from lib.api import HOJ as HOJapi
import os

def main(HOJ: HOJapi):
    """工具箱主函数"""
    os.system('cls')
    tools = HOJ.get_tools()
    if tools:
        interaction.show_message('获取工具箱失败', 'error')
        os.system('pause')
        return

    tool_list = {}
    for tool in tools:
        tool_list.update({tool['name']: tool['url']})
    
    match interaction.get_case(list(tool_list.keys()) + ['exit'], '工具箱'):
        case 'exit':
            pass
        case tool:
            os.system(f'start {tool_list[tool]}')
    