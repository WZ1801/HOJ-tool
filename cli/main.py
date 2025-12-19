from lib import api
from lib import interaction
import os
from lib.config import get_config, get_user_data

def main():
    """客户端主函数"""
    global config
    os.system('cls')
    if not config:
        interaction.show_message('配置错误', 'error')
        os.system('pause')
        return
    HOJ = api.HOJ(config['OJ']['APIURL'])
    if HOJ.login(config['OJ']['username'], config['OJ']['password']):
        # print(Fore.GREEN + f'登录成功:{HOJ.user}' + Style.RESET_ALL)
        pass
    else:
        interaction.show_message('登录失败', 'error')
        os.system('pause')
        return
        
    # while True:
    #     print(get_key())
    
    while True:
        os.system('cls')
        interaction.show_hello(HOJ.get_website_name(), HOJ.user, api.get_hitokoto())
        match interaction.get_case(["首页", "题目", "训练", "比赛", "评测", "排名", "团队", "工具箱", "exit"]):
            case "首页":
                pass
            case "题目":
                pass
            case "训练":
                pass
            case "比赛":
                pass
            case "评测":
                pass
            case "排名":
                import module.rank
                module.rank.main(HOJ)
            case "团队":
                pass
            case "工具箱":
                import module.tools
                module.tools.main(HOJ)
            case "exit":
                break

if __name__ == '__main__':
    os.system('cls')
    config = get_config()
    if not config:
        interaction.show_message('欢迎首次使用HOJ Cli,按任意键配置信息', 'info')
        os.system('pause')
        get_user_data()
        config = get_config()
        os.system('cls')
    interaction.show_message('欢迎使用HOJ Cli - HOJ tool!', 'info')
    interaction.show_message('按回车进入客户端，Ctrl+C 进入配置', 'warning')
    try:
        input()
    except KeyboardInterrupt:
        os.system('cls')
        get_user_data()
        config = get_config()
    main()
    