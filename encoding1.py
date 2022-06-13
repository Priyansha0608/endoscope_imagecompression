import numpy as np
from jpeg_compression import forward_compress
import cv2 as cv

#zig-zag encoding to convert 2-d array into 1-d array
def constructZigzagArray(mat):  
    N = mat.shape[0]
    lstResult = []
    iPlus = False
    tPlus = True
    t = 0
    j = 1
    
    while True:
        if tPlus:
            if iPlus:
                for i in range(t+1):
                    lstResult.append(mat[i, t-i])
            else:
                for i in range(t, -1, -1):
                    lstResult.append(mat[i, t-i])
            t += 1
            iPlus = not iPlus

            if t == N:
                tPlus = not tPlus
        else:
            k = t-1
            if iPlus:
                for i in range(j, t):
                    lstResult.append(mat[i, k])
                    k -= 1
            else:
                for i in range(j, t):
                    lstResult.append(mat[k, i])
                    k -= 1
            j += 1
            iPlus = not iPlus
            if j>t:
                break
    return np.array(lstResult)

def changeToHexDigit(num):
    if (num==10) or (num=='10'):
        return 'A'
    elif (num==11) or (num=='11'):
        return 'B'
    elif (num==12) or (num=='12'):
        return 'C'
    elif (num==13) or (num=='13'):
        return 'D'
    elif (num==14) or (num=='14'):
        return 'E'
    elif (num==15) or (num=='15'):
        return 'F'
    return str(num)

#finds the bit code of the first value (also largest) in the matrix
def findDCCode(DC,DC_Codes,category):
    #print(DC_Codes)
    #print(category)
    #print(DC)
    
    DC_category = None;
    for i in range(0,7):
        if(DC in category[i][1]):
            DC_category = i
            break
    #print(DC_category)
    #DC_category is DC lookup table
    
    baseCode = DC_Codes[DC_category][2]
    #print(baseCode)
    
    position = category[DC_category][1].index(DC);
    #print(position)
    
    if(position == 0):
        for i in range(DC_category):
            baseCode+='0'
    else:
        temp_code = np.binary_repr(position)
        while (len(temp_code) != DC_category):
            temp_code = '0' + temp_code 
        baseCode += temp_code
    
    #print(baseCode)
    return baseCode
        
    
def computeDctJpegCompression(imge, file):
    DC_Codes = np.loadtxt('dc_codes.txt', delimiter='\t', dtype=str)
    AC_Codes = np.loadtxt('ac_codes.txt', delimiter='\t', dtype=str)
    ac = AC_Codes.tolist()
    #print(ac)
    c = np.loadtxt('category_table.txt', delimiter='\t', dtype=str)
    category = c.tolist()
    
    #print(category) 
    for i in range(0,7): 
        category[i][1] = [int(i) for i in category[i][1].split(',')]
    
    #category and ac are lookup tables for bit length and AC values
    
    result = '' #string of bits in text file
    
    N = imge.shape[0]
    previousDC = None
    
    for i in np.arange(0, N, 8):
        for j in np.arange(0, N, 8):
            blockImgeDctQ = forward_compress(imge,i,j)
            blockImgeDctQFlat = constructZigzagArray(blockImgeDctQ)
            blockImgeDctQFlat = np.trim_zeros(blockImgeDctQFlat, trim='b')
        
            file.write(str(blockImgeDctQFlat)+'\n\n')
            file.write('Run-length symbol representation:\n')
            #DC
            if blockImgeDctQFlat.size == 0:
                DC = 0
            else:
                DC = int(blockImgeDctQFlat[0])
            if previousDC is None:
                previousDC = DC
            else:
                temp = previousDC
                DC -= previousDC
                previousDC = temp
            
            DCCode = findDCCode(DC,DC_Codes,category)
            file.write('{'+str(DCCode)+',')
            result+=DCCode
            
            #AC
            runs = 0
            for i in range(1, blockImgeDctQFlat.size):
                AC = int(blockImgeDctQFlat[i])
                
                if AC == 0:
                    runs += 1
                else:
                    #figure out category
                    AC_category = None
                    for i in range(0,7):
                        if(AC in category[i][1]):
                            AC_category = i
                            break
                    if(runs>9):
                        runs = 9
                    #figure out baseCode
                    indx = runs*11+AC_category
                    baseCode = AC_Codes[indx][3]
                    
                    position = category[AC_category][1].index(AC);
                    #print(position)
                    
                    if(position == 0):
                        for i in range(AC_category):
                            baseCode+='0'
                    else:
                        temp_code = np.binary_repr(position)
                        while (len(temp_code) != AC_category):
                            temp_code = '0' + temp_code 
                        baseCode += temp_code
                    
                    file.write(str(baseCode)+',')
                    result+=baseCode
                    runs = 0
            #add EOB
            file.write('EOB}\n\n')
            result += AC_Codes[0, 3]
    return result, len(result) 

if __name__ == '__main__':
    image = cv.imread('flower.png')
    print(image.shape)
    image1 = image.copy()
    img = cv.cvtColor(image, cv.COLOR_BGR2YCrCb)
    
    file_delete = open('file4.txt', 'w')
    file = open('r.txt','w')
    
    y, cr, cb = cv.split(img)
        
    row = image.shape[0]
    col = image.shape[1]
    
    (y_result,y_len) = computeDctJpegCompression(y,file_delete)
    file.writelines(y_result)
    print(y_len)
    #(g_result,g_len) = computeDctJpegCompression(g)
    #(r_result,r_len) = computeDctJpegCompression(r)
    
    file_delete.close()
    file.close()
        