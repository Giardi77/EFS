import argparse
from ipaddress import ip_address
import os

def list_of_strings(arg):
    return arg.split(',')
 
parser = argparse.ArgumentParser(prog='EFT', description='Encrypted File Transfer')
parser.add_argument('-t','--type',choices=['listen','send'],required=True,help='Choose what to do with this machine, "listen" to recieve data or "send" to send data')
parser.add_argument('-a','--address',required=True,type=ip_address,help=" ip to listen on or send to")
parser.add_argument('-p','--port',default=8954,type=int,help='Port to listen on or send to (default: 8954)')
parser.add_argument('-b','--bits',default=4096,choices=[4096,6144,8192],help='Choose bit lenght for the random p, g and a for diffie-helman key exchange process')
parser.add_argument('-o', '--output', default=os.getcwdb(),type=str,help='Choose where to put recieve files')
parser.add_argument('-f','--file',type=list_of_strings,help='Choose a file to send or a list of files, separated by a comma whitespace')

args = parser.parse_args()

ADDRESS = (args.address.__str__(),args.port)
OUTPUT = args.output
FILES = args.file
lunghezza_bit = args.bits

def parse_files(files_argument) -> list:
    files = []

    for f in files_argument:
        if os.path.isdir(f):
            files += get_all_files(f)
        else:
            files.append(f)
    
    return files

def get_all_files(directory_path) -> list:
    files_list = []
    
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # Join the root path with the file name to get the full path
            full_path = os.path.join(root, file)
            files_list.append(full_path)
    
    return files_list


if __name__ == '__main__':
    if args.type == 'listen': 
        from connection.listen import listener
        listener(ADDRESS)

    if args.type == 'send': 
        from connection.send import sender
        if FILES:
            sender(ADDRESS,lunghezza_bit,parse_files(FILES)) 
        else:
            print('Please specify file or files to send with --file of -f and a list of files separate by whitespace')