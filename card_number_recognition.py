import cv2
import numpy as np

def sequence_contours(image,width,height):
    # 搜索图片外轮廓，例如数字6，需要EXTERNAL搜索方式
    contours,hierarchy = cv2.findContours(image,
                                          cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)
    # 每个数字都是由x,y,w,h组成的矩阵，n个数字就是n行4列的矩阵
    n = len(contours)
    RectBoxes0 = np.ones((n,4),dtype=int)
    for i in range(n):
        # 把每个数字轮廓x,y,w,h四个值，存入RectBoxes0
        RectBoxes0[i] = cv2.boundingRect(contours[i])

    # 数字排序
    RectBoxes = np.ones((n,4),dtype=int)
    # RectBoxes0 x坐标跟各行x坐标对比，并把最小值存入存入RectBoxes
    for i in range(n):
        sequence = 0
        for j in range(n):
            if RectBoxes0[i][0]>RectBoxes0[j][0]:
                sequence = sequence+1
        RectBoxes[sequence]=RectBoxes0[i]

    ImgBoxes = [[] for i in range(n)]
    for i in range(n):
        x,y,w,h = RectBoxes[i]
        # 将排序后的矩阵，转化为对应的图片区域
        ROI = image[y:y+h,x:x+w]
        # 目标与模板尺寸大小要一致
        ROI = cv2.resize(ROI,(width,height))
        # 图片尺寸被重置后，像素点会模糊，需要进行二值化处理
        thresh_val,ROI = cv2.threshold(ROI,200,255,cv2.THRESH_BINARY)
        # 处理后的图片区域，存入列表后返回
        ImgBoxes[i] = ROI

    return RectBoxes,ImgBoxes


def CradNumRecognition():
    ## 原图片
    '''
    card_num = cv2.imread('bank_card4.jpg')
    cv2.imshow('card_num',card_num)
    '''


    ## 灰度处理
    card_GRAY = cv2.imread('bank_card41.jpg',0)
    # card_GRAY.shape[1]图片宽度
    # card_GRAY.shape[0]图片长度
    card_GRAY4 = cv2.resize(card_GRAY,(4*card_GRAY.shape[1],4*card_GRAY.shape[0]))
    cv2.imshow('card_GRAY4',card_GRAY4)


    ## 二值化处理
    # 全局阈值
    '''
    thresh_val,thresh = cv2.threshold(card_GRAY4,100,255,cv2.THRESH_BINARY_INV)
    cv2.imshow('thresh',thresh)
    '''
    # 自适应阈值
    # 减少领域大小，可以使数字轮廓更加完整(减少割裂、凸起...) 21->13
    adaptiveThresh =cv2.adaptiveThreshold(card_GRAY4,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,13,3)
    cv2.imshow('adaptiveThresh',adaptiveThresh)


    ## 轮廓筛选
    contours,hierarchy = cv2.findContours(adaptiveThresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # contours是所有轮廓的列表，需要对每个轮廓逐一填充
    for i in range(len(contours)):
        # 判断每个轮廓的面积，小于一定面积采取填充
        if cv2.contourArea(contours[i])<160:
            adaptiveThresh = cv2.drawContours(adaptiveThresh,contours,i,(0,0,0),-1)
    cv2.imshow('adaptiveThresh',adaptiveThresh)


    ## 形态学变化
    # 采用黑帽方法，需要凸显图像前景内的孔洞
    # 数字作为孔洞，矩阵需要设置较大的值
    kernel = np.ones((15,15),dtype=np.uint8)
    blackhat = cv2.morphologyEx(adaptiveThresh,cv2.MORPH_BLACKHAT,kernel)
    cv2.imshow('blackhat',blackhat)

    # 数字与背景白色有相连，为了保证数字完整性，使用开运算去除背景中的白色噪音
    # 由于是背景白色降噪处理，矩阵需要设置较小的值
    kernel = np.ones((3,3),dtype=np.uint8)
    opening = cv2.morphologyEx(blackhat,cv2.MORPH_OPEN,kernel)
    cv2.imshow('opening',opening)

    # 用数字面积比较的方法，把背景中较大的白色噪音填充为黑色
    contours,hierarchy = cv2.findContours(opening,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for i in range(len(contours)):
        x,y,w,h = cv2.boundingRect(contours[i])
        # 每个轮廓宽度和高度比值
        aspect_ratio = float(w)/h
        # 每个轮廓面积
        Area = w*h
        if Area < 1800 or Area > 6000:
            opening = cv2.drawContours(opening,contours,i,(0,0,0),-1)
        else:
            if aspect_ratio > 0.7 or aspect_ratio < 0.5:
                opening = cv2.drawContours(opening,contours,i,(0,0,0),-1)
    cv2.imshow('opening',opening)

    # 为了让数字粗细更接近模板图片
    # 使用膨胀的方式，使数字加粗
    kernel = np.ones((5,5),dtype=np.uint8)
    dilation = cv2.dilate(opening,kernel,iterations=1)
    cv2.imshow('dilation',dilation)


    ## 模板图片灰度处理
    numTemplate = cv2.imread('bankCardNumTemplate.jpg',0)
    # 模板图片二值化处理(全局阈值)
    ret,numTemplate_GRAY = cv2.threshold(numTemplate,200,255,cv2.THRESH_BINARY)
    #cv2.imshow('numTemplate_GRAY',numTemplate_GRAY)

    ## 数字截取与排序
    # 模板图片数字截取与排序
    # RectBoxes_Temp存储x,y,w,h矩阵，ImgBoxes_Temp存储处理后图片数字
    RectBoxes_Temp,ImgBoxes_Temp = sequence_contours(numTemplate_GRAY,50,80)
    #print(RectBoxes_Temp)
    #cv2.imshow('ImgBoxes_Temp',ImgBoxes_Temp[1])
    # 目标图片数字截取与排序
    RectBoxes,ImgBoxes = sequence_contours(dilation,50,80)
    #print(RectBoxes)
    #cv2.imshow('ImgBoxes',ImgBoxes[1])


    ## 模板匹配
    result = []
    for i in range(len(ImgBoxes)):
        # 初始化结果列表，长度与ImgBoxes_Temp一致
        score = np.zeros(len(ImgBoxes_Temp),dtype=int)
        for j in range(len(ImgBoxes_Temp)):
            # 每个数字对比结果存入列表
            score[j] = cv2.matchTemplate(ImgBoxes[i],ImgBoxes_Temp[j],cv2.TM_SQDIFF)
        # 找出score列表中最小值的信息
        min_val,max_val,min_indx,max_indx = cv2.minMaxLoc(score)
        result.append(str(min_indx[1]))

    print(''.join(result))

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    CradNumRecognition()