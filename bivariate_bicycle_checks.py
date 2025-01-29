from typing import List
from numpy import array, kron, concatenate, zeros,eye
from numpy.linalg import matrix_power


def Smatrix(n:int):
    Sm = zeros(shape = (n,n),dtype = int)
    for i in range(n):
        Sm[i,(i+1)%n] = 1
    return Sm

def xmatrix(el:int,m:int):
    return array(kron(Smatrix(el),eye(m)),dtype=int)

def ymatrix(el:int,m:int):
    return array(kron(eye(el),Smatrix(m)),dtype=int)

def Amatrix(m:int,el:int,ax:int,ay1:int,ay2:int):

    X = xmatrix(m,el)
    Y = ymatrix(m,el)

    A1 = matrix_power(X,ax)
    A2 = matrix_power(Y,ay1)
    A3 = matrix_power(Y,ay2)

    # A1 = X**ax
    # A2 = Y**ay1
    # A3 = Y**ay2

    return array((A1+A2+A3),dtype = int)

def Bmatrix(m:int,el:int,by:int,bx1:int,bx2:int):

    X = xmatrix(m,el)
    Y = ymatrix(m,el)

    B1 = matrix_power(Y,by)
    B2 = matrix_power(X,bx1)
    B3 = matrix_power(X,bx2)

    # B1 = Y**by
    # B2 = X**bx1
    # B3 = X**bx2

    return array((B1+B2+B3),dtype=int)

def pcm(m:int,el:int,aexp = List[int],bexp = List[int]):

    ax,ay1,ay2 = aexp
    by,bx1,bx2 = bexp

    A = Amatrix(m,el,ax,ay1,ay2)
    B = Bmatrix(m,el,by,bx1,bx2)

    Hx = concatenate((A,B),axis=1)
    Hz = concatenate((B.T,A.T),axis=1)

    return Hx,Hz
    
