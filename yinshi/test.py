__author__ = 'Administrator'
#coding=utf-8
import json,sys,shutil,os,logging
reload(sys)
sys.setdefaultencoding( "utf-8" )
logging.basicConfig(level=logging.DEBUG,
                    format=' %(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='weibo.log',
                    filemode='a')

def json2text(file_name):
    file_read = open(file_name,"r")
    file_write = open(file_name+".txt","w")
    for line in file_read:
        try:
            line = line.strip().split("	")
            if len(line) == 2:
                id = line[0]
                a = json.loads(line[1])
                gender = a['user']['gender']
                location = a['user']['location']
                # name = a['user']['name']
                # daren = a['user']['daren']
                # tags = a['user']['tags']
                # verified = a['user']['verified']
                friendsCount = a['user']['friendsCount']
                # followersCount = a['user']['followersCount']
                # id = a["id"]
                # print a["comments"]
                for item in a["statuses"]:
                    code = id+"\t\t"+item["text"]+"\t\t"+item["createdAt"]+"\t\t"+location+"\t\t"+gender+"\n"
                    # code.decode("utf-8").encode("utf-8")
                    file_write.write(code)
                    # print id,item["text"],item["createdAt"],location,gender
        except Exception:
            pass

    file_read.close()
    file_write.close()

file =  os.listdir("/users3/nlp-data/weibo")
for item in file:
    if item.find(".gzip") != -1:
        logging.info("begin copy:"+item)
        src = os.path.join("/users3/nlp-data/weibo",item)
        dis = os.path.join("/users3/nlp-data/scr",item.replace(".gzip",".gz"))
        shutil.copyfile(src,dis)
        logging.info("begin unzip:"+item)
        os.system("gzip -d "+ dis)
        logging.info("begin json2text:"+item)
        json2text(os.path.join("/users3/nlp-data/scr",item.replace(".gzip","")))
        os.remove(os.path.join("/users3/nlp-data/scr",item.replace(".gzip","")))

logging.info("end:"+item)

