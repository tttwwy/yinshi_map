#coding=utf-8
import sys,re,subprocess,xml.etree.ElementTree as etree,os,Queue,time,math,logging
# from langconv import *
import multiprocessing

reload(sys)
sys.setdefaultencoding( "utf-8" )
__author__ = 'WangZhe'

logging.basicConfig(level=logging.DEBUG,
                    format=' %(process)d: %(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='yinshi.log',
                    filemode='a')


tbfWord = ("吃".decode('utf-8'),"喝".decode('utf-8') )
xml_origin = {}
queue = Queue.PriorityQueue()
def pickup_file(file_name):
    file = open(file_name,"r")
    file_write = open(file_name+"_ban","w")
    xml_index = 0

    for index,line in enumerate(file):
        id,uid,content,time,flag,username,male,location = line.strip().split("\t")

        content = ban_rubbish(content)
        if content == "":
            continue

        for item in split_sentence(content):
            for word in tbfWord:
                if item.decode('utf-8').find(word) != -1:
                    item = Converter('zh-hans').convert(item.decode('utf-8')).encode('utf-8')
                    file_write.write(item + "\n")
                    xml_origin[xml_index] = index
                    xml_index += 1
                    break

    file.close()
    file_write.close()
    return file_name+"_ban"


def split_sentence(content):
    # punt_list =  '.!?:;~。！？?…#：；～ ~!&"“”，,'.decode('utf-8')
    punt_list =  '.!?;~。！？?…#；～ &~!'.decode('utf-8')
    # content = content.decode('utf-8')
    sentences = []
    sentence = ""

    for item in content.decode('utf-8'):
        if item in punt_list:
            if len(sentence) > 3:
                sentences.append(sentence.encode('utf-8'))
            sentence = ""
        else:
            sentence += item

    if len(sentence) > 3:
        sentences.append(sentence.encode('utf-8'))
    return sentences





def ban_rubbish(content):
    if re.search(".*http://.*",content):
        return ""
    if re.search("【.*】",content):
        return ""

    m = re.findall("[\d①②③④]",content)
    if len(m) > 3:
        return ""

    content =  re.subn("\[.*\]","",content)[0]
    content = re.subn("//@.*","",content)[0]
    content = re.subn("//@.* ","",content)[0]

    return content

def word_split_file(file_name):
    fdout = open(file_name + "_ws_temp", 'w')
    fderr = open(file_name +"_ws.err", 'w')
    fdin = open(file_name,'r')
    popen = subprocess.Popen("/users1/exe/bin/weicws",stdin=fdin,stdout=fdout,stderr=fderr, shell=True)
    popen.wait()
    fdout.close()

    fdin = open(file_name + "_ws_temp", 'r')
    fdout = open(file_name + "_ws", 'w')
    for line in fdin:
        fdout.write(line.replace("\t"," "))
    fdout.close()
    os.remove(file_name + "_ws_temp")
    return file_name + "_ws"

def dp_file(file_name):
    fdout = open(file_name + "_dp", 'w')
    fderr = open(file_name +"_dp.err", 'w')
    popen = subprocess.Popen(["/users1/exe/bin/multi_ltp_test_wsed","/data/yjliu/ltp-models/3.0.2/ltp.cnf","dp",file_name],
                             stdout=fdout,stderr=fderr, shell=False)
    popen.wait()
    return file_name +"_dp"




def xml_parse(content):
    nodes = []
    parser = etree.XMLParser(encoding="utf-8")

    tree = etree.fromstring(content,parser=parser)
    for node in tree.iter("word"):  #遍历解析树
        nodes.append({"id":node.attrib.get("id"),
                     "cont":node.attrib.get("cont"),
                     "pos":node.attrib.get("pos"),
                     "parent":node.attrib.get("parent"),
                     "relate":node.attrib.get("relate")})

    # for i in range(1,len(nodes) ):
    #     if nodes[i-1]["pos"].find("n") != -1 and nodes[i]["pos"].find("n") != -1:
    #         if nodes[i-1]["parent"] == nodes[i]["id"] or nodes[i-1]["parent"] == nodes[i]["parent"]:
    #             nodes[i]["cont"] = nodes[i-1]["cont"] + nodes[i]["cont"]
    #             nodes[i-1]["relate"] = ""
    #
    #             for node in nodes:
    #                 if node["parent"] == nodes[i-1]["id"]:
    #                     node["parent"] = nodes[i]["id"]

    result = []
    for node in nodes:
        if node["relate"] == "VOB" \
                and node["pos"].find("n") != -1 \
                and (nodes[int(node["parent"])]["cont"] == "喝" or nodes[int(node["parent"])]["cont"] == "吃"):
            result.append(node["cont"])

    return result

def xml_file(file_name):
    file = open(file_name,'r')
    content = ""
    state = 0
    xml_index = 0
    for line in file:
        if line == "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n":
            # print "haha"
            if len(content) > 0:
                try:
                    words = xml_parse(content)
                    for word in words:
                        queue.put((xml_origin[xml_index],word))
                except Exception:
                    print "error!!!"
                finally:
                    xml_index += 1
                    content = ""

        else:
            content += line
    if len(content) > 0:
        # print content
        word = xml_parse(content)
        for item in word:
            if item:
                queue.put((xml_origin[xml_index],item))
    file.close()

def get_final(file_name):
    file = open(file_name,"r")
    file_write = open(file_name+"_result","w")
    # print queue._qsize()
    if not queue.empty():
        index,word = queue.get()
        for cur_index,line in enumerate(file):
            while cur_index == index:
                file_write.write(word+"\t"+ line)
                if queue.empty():
                    file.close()
                    file_write.close()
                    return
                else:
                    index,word = queue.get()

            if cur_index > index:
                if queue.empty():
                    break
                else:
                    index,word = queue.get()
    file.close()
    file_write.close()

def worker(file,id):
    logging.info("%s pickup begin"%(file))
    file_name = pickup_file(file)
    logging.info("%s word_split begin"%(file))
    file_name = word_split_file(file_name)
    logging.info("%s dp begin"%(file))
    file_name = dp_file(file_name)
    logging.info("%s xml parse begin"%(file))
    xml_file(file_name)
    logging.info("%s final begin"%(file))
    get_final(file)



start = time.time()
logging.info("begin:")
sum_line = 0
file = open(sys.argv[1],"r")
for line in file:
    sum_line += 1

thread_num = int(sys.argv[2])
offset = int( (sum_line + thread_num - 1)/ thread_num )
file.close()

logging.info("line:%d offset:%d"%(sum_line,offset))
file = open(sys.argv[1],"r")

# offset = 100000
logging.info("thread_num:%d"%(thread_num))
num = 0
f = open(sys.argv[1]+"_"+str(num),"w")
file_list = []
for index,line in enumerate(file):
    if index % offset == 0:
        f.close()
        f = open(sys.argv[1] + "_" + str(num),"w")
        file_list.append(sys.argv[1] + "_" + str(num))
        num += 1
    f.write(line)
f.close()

jobs = []
for index,file in enumerate(file_list):
    p = multiprocessing.Process(target=worker,args=(file,index))
    jobs.append(p)
    p.start()

for job in jobs:
    job.join()

file_write = open(sys.argv[1]+"_result","w")
for file_name in file_list:
    file_read = open(file_name+"_result","r")
    for line in file_read:
        file_write.write(line)
    file_read.close()
file_write.close()

end = time.time()
logging.info("end process \n time cost:%d"%(end-start))

