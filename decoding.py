import numpy as np
from jpeg_compression import forward_compress
import cv2 as cv

#zig-zag encoding to convert 2-d into 1-d 
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
    
    baseCode = DC_Codes[DC_category][2]
    #print(baseCode)
    
    position = category[DC_category][1].index(DC);
    #print(position)
    
    if(position == 0):
        baseCode+='0'
    else: 
        baseCode += np.binary_repr(position)
    
    #print(baseCode)
    return baseCode
        
    
def computeDctJpegDecompression(result, file):
    DC_Codes = np.loadtxt('dc_codes.txt', delimiter='\t', dtype=str)
    AC_Codes = np.loadtxt('ac_codes.txt', delimiter='\t', dtype=str)
    c = np.loadtxt('category_table.txt', delimiter='\t', dtype=str)
    
    cat = c.tolist()
    for i in range(0,7): 
        cat[i][1] = [int(i) for i in cat[i][1].split(',')]
    
    dccat_code = []
    for i in range(0,7):
        dccat_code.append(DC_Codes[i][2])
        
    accat_code = []
    for i in AC_Codes:
        accat_code.append(i[3])
    
    print(accat_code)
    mat = []
    firstDC = None
    code = result[0]
    looking_EOB = False
    
    print(len(result))
    i=0
    while (i!= len(result)):
        #DC Code
        if(code in dccat_code and not looking_EOB):
            category = dccat_code.index(code)
            
            value = None
            if(category == 0):
                value = 0
            else: 
                position_code = ''
                for j in range(category):
                    position_code += result[i+j+1]
                i=i+j+1
                position = int(position_code, 2)
                value = cat[category][1][position]
                
            if(firstDC == None):
                firstDC = value
            else: 
                value+=firstDC
            
            mat.append(value)
            code = ''
            looking_EOB = True
        
            #file.write(str(value))
        elif(code in accat_code and looking_EOB):
            if(code == '1010'):
                file.write(str(mat))
                file.write(' EOB\n\n')
                
                #change from 2D to 1D
                #reverse transform the 2D matrix
                #update imgmat
                
                mat = []
                code = ''
                looking_EOB = False
            else:
                indx = accat_code.index(code)
                category = indx%11
                run = (indx-category)/11
                
                while(run>0):
                    mat.append(0)
                    run-=1
                
                position_code = ''
                for j in range(category):
                    position_code += result[i+j+1]
                i=i+j+1
                position = int(position_code, 2)
                value = cat[category][1][position]
                
                mat.append(value)
                code = ''
        else:
            i+=1
            if(i == len(result)):
                break
            code += result[i]

if __name__ == '__main__':
    file_delete = open('file5.txt', 'w')
    file = open('r.txt','r')
    
    computeDctJpegDecompression(file.readline(),file_delete)
    #file.writelines(y_result)
    #(g_result,g_len) = computeDctJpegCompression(g)
    #(r_result,r_len) = computeDctJpegCompression(r)
    
    file_delete.close()
    file.close()
