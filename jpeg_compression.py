import cv2 as cv
from scipy import fftpack,special
import numpy

Q50 = numpy.array(
      [[16, 11, 10, 16, 24, 40, 51, 61],
       [12, 12, 14, 19, 26, 58, 60, 55],
       [14, 13, 16, 24, 40, 57, 69, 56],
       [14, 17, 22, 29, 51, 87, 80, 62],
       [18, 22, 37, 56, 68, 109, 103, 77],
       [24, 35, 55, 64, 81, 104, 113, 92],
       [49, 64, 78, 87, 103, 121, 120, 101],
       [72, 92, 95, 98, 112, 100, 103, 99]])

Q50 = Q50.astype(numpy.float64)
recip_Q50 = numpy.reciprocal(Q50)

dct_matrix8 = fftpack.dct(numpy.identity(8),2,None,-1,'ortho')
inverse_dct_matrix8 = fftpack.idct(numpy.identity(8),2,None,-1,'ortho')

def forward_compress(imge, x, y):
    #extract 8x8 pixel starting at (x,y)
    #for i in range(x,len):
    #    for j in range(y,len):
    matrix = _8_8(imge,x,y)
    dct_domain = numpy.matmul(numpy.matmul(dct_matrix8,matrix),inverse_dct_matrix8) # forward dct
    dct_quantized = quantization(dct_domain)
    
    return dct_quantized        

def backward_compress(mat,x,y,image):
    dct_dequantized = dequantization(mat)
    dct_restored = numpy.matmul(numpy.matmul(inverse_dct_matrix8,dct_dequantized),dct_matrix8) # inverse dct
    image = change_image(image,dct_restored,x,y)
    
    return image
'''
def forward_compress(image,r,c):
    image_copy = numpy.copy(image)
    i = 0
    j = 0
    while i < r: 
        while j < c:           
            matrix = _8_8(image_copy,i,j) #also subtracts pixel value by 128
            dct_domain = numpy.matmul(numpy.matmul(dct_matrix8,matrix),inverse_dct_matrix8) # forward dct
            dct_quantized = quantization(dct_domain)
            
            #take all the values and create a frequency dictionary of numbers
            #create huffman tree
            
            #huffman using huffman tree
            #decode using huffman tree
            
            #dct_dequantized = dequantization(dct_quantized)
            #dct_restored = numpy.matmul(numpy.matmul(inverse_dct_matrix8,dct_dequantized),dct_matrix8) # inverse dct
            #image_copy = change_image(image_copy,dct_restored,i,j)
            j+=8
        i+=8
        j=0 
    #return image_copy
    return dct_quantized
'''
def dequantization(matrix):
    return numpy.multiply(Q50,matrix)

def quantization(matrix):
    return special.round(numpy.multiply(recip_Q50,matrix))

def change_image(image,matrix,i,j):
    for k in range(8):
        for l in range(8):
            # maybe a better/faster way to do this?
            pixel = matrix[k][l]
            if pixel < 0: 
                pixel = 0
            if pixel > 255: 
                pixel = 255
            image[k+i][l+j] = pixel
    return image

def _8_8(image,i,j):
    matrix = []
    for p in range(8):
        inner_matrix = []
        for q in range(8):
            inner_matrix.append(image[i+p][j+q])
        matrix.append(inner_matrix)
    return matrix    
                  
if __name__ == '__main__':
    image = cv.imread('hidef.jpeg')
    print(image.shape)
    image1 = image.copy()
    b,g,r = cv.split(image)
    
    row = image.shape[0]
    col = image.shape[1]
    
    #so it fits 8x8 boxes
    if not row % 8 == 0:
        row = 8*(row//8)
    if not col % 8 == 0: 
        col = 8*(col//8)
    
    #b_image = compress(b,row,col)
    #g_image = compress(g,row,col)
    #r_image = compress(r,row,col) 
    #image2 = cv.merge([b_image,g_image,r_image])
    
    #cv.imshow('b',b)
    #cv.imshow('b_img',b_image)
    #cv.imshow('r',r)
    #cv.imshow('r_img',r_image)
    #cv.imshow('g',g)
    #cv.imshow('g_img',g_image)
    #cv.imshow('Changed',image2)
    cv.imshow('Original',image1)
    
    cv.waitKey(0)
    cv.destroyAllWindows()
    
