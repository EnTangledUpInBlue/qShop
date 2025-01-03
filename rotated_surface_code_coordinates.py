from typing import List,Set,Dict,Tuple

def rsurf_qubit_coords(L:int) -> Set[Tuple[int,int]]:

    if L==1:
        return set([(0,0)])
    
    else:
        Lset = rsurf_qubit_coords(L-1)
        for coord1 in range(L-2,L):
            Lset.add((2*coord1,2*coord1))

            for coord2 in range(coord1):
                Lset.add((2*coord1,2*coord2))
                Lset.add((2*coord2,2*coord1))
        
        return Lset

def rsurf_check_coords(L:int) -> List[Set[Tuple[int,int]]]:

    if L==3:
        xcheck_coords = {(-1,1), (1,3), (3,1), (5,3)}

        zcheck_coords = {(1,1),(1,5),(3,-1), (3,3)}

        return [xcheck_coords,zcheck_coords]
    
    else:
        xcheck_coords,zcheck_coords = rsurf_check_coords(L-2)

        z1 = (1,2*L-1)
        z2 = (2*L-3,-1)
        dy = [-2,2]

        zcheck_coords.add(z1)
        zcheck_coords.add(z2)

        for ii in range(L-2):
            z1 = (z1[0]+2,z1[1]+dy[ii%2])
            z2 = (z2[0]+dy[ii%2],z2[1]+2)

            zcheck_coords.add(z1)
            zcheck_coords.add(z2)            

        x1 = (-1,2*L-5)
        x2 = (2*L-3,1)
        dx = [2,-2]

        xcheck_coords.add(x1)
        xcheck_coords.add(x2)

        for ii in range(L-2):
            x1 = (x1[0]+2, x1[1]+dx[ii%2])
            x2 = (x2[0]+dx[ii%2],x2[1]+2)
            xcheck_coords.add(x1)
            xcheck_coords.add(x2)

        return xcheck_coords,zcheck_coords

