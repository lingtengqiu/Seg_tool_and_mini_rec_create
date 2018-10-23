import cv2
import numpy as np
import glob
import dataTransform
import sys
import tqdm
def get_rect_only(img_name):
    dt = dataTransform.dataTransform()
    mask = cv2.imread(img_name,0)
    mask[mask>0] = 255
    x,y,w,h = cv2.boundingRect(mask)
    queue =[]
    go = np.zeros(shape=mask.shape)
    sets = set()
    #kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(125, 125))
    #mask = cv2.dilate(mask,kernel)
    #mask = cv2.erode(mask,kernel)
    bnd_info =[]
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if(mask[i][j] == 0):
                go[i][j] = 1
            elif(go[i][j] == 0):
                temp = np.zeros(mask.shape)
                queue =[]
                queue.append((i,j))
                while(len(queue)!=0):
                    y,x = queue.pop(0)
                    temp[y][x] = 255
                    if(y-1>=0):
                        if(go[y-1][x] == 0 and mask[y-1][x] ==255):
                            go[y-1][x] = 1
                            queue.append((y-1,x))                            
                    if(y+1<mask.shape[0]):
                        if(go[y+1][x] == 0 and mask[y+1][x] ==255):
                            go[y+1][x] = 1
                            queue.append((y+1,x))
                    if(x-1>=0):
                        if(go[y][x-1] == 0 and mask[y][x-1] ==255):
                            go[y][x-1] = 1
                            queue.append((y,x-1))
                    if(x+1<mask.shape[1]):
                        if(go[y][x+1] == 0 and mask[y][x+1] ==255):
                            go[y][x+1] = 1
                            queue.append((y,x+1)) 
                y,x = np.where(temp>0)
                ymin = np.min(y)
                ymax = np.max(y)
                xmin = np.min(x)
                xmax = np.max(x)
                bnd_info.append([0,xmin,ymin,xmax,ymax]) 
    dt.writeXml(img_name,"./xmlfiles",mask,bnd_info)

            

if __name__ =="__main__":
    mask_names = glob.glob(sys.argv[1]+"*")
    for i in tqdm.tqdm(mask_names):
        get_rect_only(i)

