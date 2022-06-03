银行卡号识别笔记  
=  
## 模板匹配: 图片各对应位置像素点的对比
    cv2.matchTemplate(img,img_Temp,cv2.TM_SQDIFF)  
    img: 目标图片  
    img_Temp: 模板图片  
    cv2.TM_SQDIFF: 平方差对比。平方差越小，2个图片越接近  
    匹配目标发生旋转或大小变化，该算法无效

### 图片预处理方法: 
1.二值化(全局阈值，自适应阈值)  
2.轮廓筛选  
3.形态学变化    
<br>
####1.二值化处理
##### 全局阈值
    thresh,dst = cv2.threshold(src,thresh,maxVal,type)
    thresh:阈值，dst:二值化后的图片
    src:输入图片
    thresh:阈值
    maxVal:最大值
    type:二值化类型
    
    两种二值化类型    
    cv2.THRESH_BINARY
        if src(x,y) > thresh: maxVal
        else: 0
    
    cv2,THRESH_BINARY_INV
        if src(x,y) > thresh: 0
        else: maxVal
    
##### 自适应阈值
    cv2.adaptiveThreshold(src,maxVal,adaptiveMethod,type,blockSize,C)
    src:输入图片
    maxVal:最大值
    adaptiveMethod:自适应方法
    type:二值化类型
    blockSize:领域大小
    C:常数
    
    25 75  225
    35 65  125
    50 100 110
    adaptiveMethod=cv2.ADAPTIVE, blockSize=3, C=10, type=cv2.THRESH_BINARY
    thresh = 9个平均灰度 - C
           = 125-10 = 115
    if src(x,y) > thresh: maxVal
    else: 0

####2.轮廓筛选
##### 查找轮廓 
    contours,hierarchy = cv2.findContours(image,mode,method)
    contours:轮廓列表 [array([[[x,y]],[[x,y]],...],dtype=int32),array()]
    image:图片(灰度或二值图片)
    mode:轮廓检索模式
        cv2.RETR_EXTERNAL: 检测外轮廓
        cv2.RETR_TREE: 等级树结构的轮廓
    method:轮廓近似方法
        cv2.CHAIN_APPROX_NONE: 所有点
        cv2.CHAIN_APPROX_SIMPLE: 直线两端点
##### 绘制轮廓
    img = cv2.drawContours(image,contours,i,color,thickness)
    image:绘制轮廓的图片
    contours:轮廓列表    
    i:列表中，第i个轮廓(-1表示所有轮廓)
    color:绘制颜色
    thickness:绘制线条粗细(-1表示填充)
    
####3.形态学变化 
##### 腐蚀
    cv2.erode(image,kernel,iterations)
    image:图片
    kernel:腐蚀矩阵
    iterations:迭代次数
    kernel取3*3的矩阵，腐蚀会取领域像素中的最小值
    246  66  150     246  66  150
    88   216 141  -> 88   66  141
    150  66  235     150  66  235
##### 膨胀
    cv2.dilate(image,kernel,iterations)
    image:图片
    kernel:膨胀矩阵
    iterations:迭代次数
    kernel取3*3的矩阵，膨胀会取领域像素中的最大值
    246  66  150     246  66  150
    88   216 141  -> 88   246  141
    150  66  235     150  66  235
##### 形态学变化的方法(综合运用)
开运算:腐蚀->膨胀 去除背景中的白色噪音  
闭运算:膨胀->腐蚀 去除前景中的黑色孔洞  
礼帽:开运算与原图做差 显示背景中的白色噪音  
黑帽:闭运算与原图做差 显示前景中的黑色孔洞  
```
cv2.morphologyEx(image,op,kernel)
image:图片
op:形态学方法
kernel:矩阵大小
cv2.MORPH_OPEN 开运算
cv2.MORPH_CLOSE 闭运算
cv2.MORPH_TOPHAT 礼帽
cv2.MORPH_BLACKHAT 黑帽
```

### 数字截取与排序: 
思路:分别对目标图片和模板图片的数字截图，分别对截取数字进行排序，最后再一一做对比  
`cv2.matchTemplate(img,img_Temp,cv2.TM_SQDIFF)`





