import os
import time
import tkinter
from tkinter.filedialog import askopenfilename,askdirectory

import cv2
from threading import Thread, Lock

# from APPSystem.adaptionTrainer import pretrain
import tkinter.messagebox as messagebox
from tkinter import Frame, Entry, Button,StringVar, Label,OptionMenu
import json

'''
A label tool for depth data

requires:  tkinter, opencv

Usage:
1. Copy this script to the data root, then run "python LabelTool.py"
2. Select the class you want to label
3. Select the video path you want to label
4, Click start labeling button
5. If current frame belongs to the class you choose, press 1. Else press 0.
   press '<--' key to view previous frame, '-->' key to the next frame.

d: x2
t: x10
h: x100

'''

# LABEL_MAP={
# 'Dressing (Clothes/Shoes)':0,
# 'Cleaning living area':1,
# 'Grooming':2,
# 'Taking medication':3,
# 'Sniffing / Coughing':4,
# 'Talking':5,
# 'Phone call':6,
# 'Writing':7,
# 'Watching TV':8,
# 'Social isolation':9,
# 'Sitting':10,
# 'Standing':11,
# 'Moving in/out of chair/bed':12,
# 'Walking':13,
# 'Sleeping':14,
# 'Stretching':15,
# 'Exersicing':16,
# 'Smoking':17,
# 'Eating':18,
# 'Driking':19
# }

LABEL_MAP={
"没人/老人不在": -2,
"静态动作": -1,
"在做一些动作（但不属于1-15中任何一个）": 0,
"穿 脱衣服/裤子/鞋子": 1,
"拿/取/搬运/放东西": 2,
"做清洁/打扫房间": 3,
"摸脑袋/整理头发/梳妆打扮":4 ,
"搓手/擦手": 5,
"喝水": 6,
"吃药/吃东西":7 ,
"吸烟": 8,
"打喷嚏/咳嗽":9 ,
"写东西": 10,
"看电视": 11,
"使用手机：玩手机/语音视频通话等": 12,
"锻炼/运动": 13,
"和人交流/说话/玩/社交（比如打牌打麻将）": 14,
"伸懒腰/拉伸": 15,
"走动 ": 16,
"坐（包括趴卓子上）":17 ,
"站": 18,
"睡觉/躺":19 ,
"从椅子/床上起来/坐下的过渡状态": 20
}



def checkdir(p):
    if not os.path.exists(p):
        os.makedirs(p)

def save_json(save_dir,save_name,data):
    print('Saving results. Please wait....')
    filename=os.path.join(save_dir,save_name)
    with open(filename, 'w') as fp:
        json.dump(data, fp)
    print(f'Results are saved to {filename}')
    print(f'Please continue...')




class Application():
    def __init__(self,win_size='400x500',opt_list=[]):
        self.win_size=win_size
        self.root = tkinter.Tk()
        self.root.geometry(self.win_size)

        self.path = StringVar()
        self.action_class=StringVar()
        self.action_class.set(opt_list[0])
        OptionMenu( self.root , self.action_class , *opt_list ).grid(row = 0, column = 0)
        Label(self.root,text = "Target path:").grid(row = 1, column = 0)
        Entry(self.root, textvariable = self.path).grid(row = 1, column = 1)
        Button(self.root, text = "Select data folder", command = self.selectPath).grid(row = 1, column = 2)
        Button(self.root, text = "Start labeling", command = self.start_labeling).grid(row = 1, column = 3)

        self.root.mainloop()

    def selectPath(self):
        path_ = askdirectory(initialdir='/mnt/ssd/data/depth')
        self.path.set(path_)

    def set_label(self,gt,frame_idx,speed,label):
        st=int(max(frame_idx-speed+1,0))
        ed=int(frame_idx+1)

        print(f'#########start from {st} to {ed}...')
        for idx in range(st,ed):
            if idx in list(gt.keys()) and (gt[idx]==0 or gt[idx]==1 or gt[idx]==2):
                print('Have some duplicated labels, ignores.')
            else:
                gt[idx]=label
        return gt

    def load_ground_truth_file(self,label_dir,gt_name):
        json_path=os.path.join(label_dir,gt_name)
        # 判断 json_path是否存在，
        # 如果json_path不存在，则 return {}
        # 否则加载 json文件，存储到dict中，返回加载的dict
        if not os.path.exists(json_path):
            return {}
        else:
            with open(json_path, 'r') as fp:
                gt = json.load(fp)
            return gt
        



    def label_one(self,v_dir,vname,label_dir):
        v_path=os.path.join(v_dir,vname)
        print('Processing ',v_path)
        checkdir(label_dir)
        gt_name=vname[:-4]+'#'+str(LABEL_MAP[self.action_class.get()])+'.json'
        #gt={}
        gt=self.load_ground_truth_file(label_dir,gt_name) # ground truth
        cap = cv2.VideoCapture(v_path)
        frame_count=cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        frame_no=0
        st_time=time.time()
        speed=1
        while True:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret,frame=cap.read()
            if not ret:
                print(f'Read frame {frame_no} error')
                break
            fps=round(frame_no/(time.time()-st_time),2)
            lab='NO'
            if frame_no in list(gt.keys()):
                lab=gt[frame_no]

            message = f'{frame_no}|{frame_count-1}, FPS:{fps} | cur label:[{lab}]'
            cv2.putText(frame, message, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0),thickness=2)
            cv2.putText(frame, f'speed: {speed}', (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0),thickness=2)

            cv2.imshow('Depth Map',frame)
            key=cv2.waitKey(100000)
            print(key)
            if key==ord('0'):
                print('0 is pressed')
                self.set_label(gt,frame_no,speed,0)
                frame_no=min(frame_no+speed,frame_count-1)
            elif key==ord('1'):
                print('1 is pressed')
                self.set_label(gt,frame_no,speed,1)
                frame_no=min(frame_no+speed,frame_count-1)
            elif key==ord('2'):
                print('2 is pressed')
                self.set_label(gt,frame_no,speed,2)
                frame_no=min(frame_no+speed,frame_count-1)
            elif key==2: # left
                speed=1
                frame_no=max(frame_no-1,0)
            elif key==3: # right
                speed=1
                frame_no+=1
            elif key==ord('d'):
                speed=2
            elif key==ord('t'):
                speed=10
            elif key==ord('h'):
                speed=100
            elif key==ord('q'):
                break
        save_json(label_dir,gt_name,gt)
        cap.release()
        
    def start_labeling(self):
        
        v_dir=self.path.get()
        vnames=list(os.listdir(v_dir))
        vnames=[x for x in vnames if '.avi' in x]
        print("Start labeling...# v_dir=",v_dir)
        for vname in vnames:
            label_dir=os.path.join(v_dir,'labels')
            self.label_one(v_dir,vname,label_dir)     
        cv2.destroyAllWindows()



if __name__=='__main__':
    win_size='600x500'
    options = list(LABEL_MAP.keys())
app=Application(win_size,options)




