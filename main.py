import argparse

from traffic import traffic

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='命令行参数')
    parser.add_argument('--websites', '-w', type=str, help='Tor域名文件',required=True)
    parser.add_argument('--begin', '-b', type=int, help='开始组编号',required=True)
    parser.add_argument('--end', '-e', type=int, help='结束组编号',required=True)

    args = vars(parser.parse_args())
    traffic(website=args['websites'],begin=args['begin'],end=args['end'])