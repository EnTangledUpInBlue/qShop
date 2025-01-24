from typing import List,Set,Dict,Tuple

def surf_check_coords(L:int) -> List[Set[Tuple[int,int]]]:
    r"""
    Coordinates for the check locations in the standard surface code

    :param L: The dimensions of the square lattice for the standard surface code.
    
    """

    if L==2:
        xcheck_coords = {(0,1), (2,1)}

        zcheck_coords = {(1,0),(1,3)}

        return [xcheck_coords,zcheck_coords]
    
    else:
        xcheck_coords,zcheck_coords = surf_check_coords(L-1)

        z1 = (1,2*(L-1))
        z2 = (2*(L-1)-1,0)

        dy = 2

        zcheck_coords.add(z1)
        zcheck_coords.add(z2)

        x1 = (0,2*(L-1)-1)
        x2 = (2*(L-1),1)

        dx = 2

        xcheck_coords.add(x1)
        xcheck_coords.add(x2)


        for ii in range(L-2):

            z1 = (z1[0]+dy,z1[1])
            z2 = (z2[0],z2[1]+dy)

            zcheck_coords.add(z1)
            zcheck_coords.add(z2)            

            x1 = (x1[0]+dx, x1[1])
            x2 = (x2[0],x2[1]+dx)
        
            xcheck_coords.add(x1)
            xcheck_coords.add(x2)

        return [xcheck_coords,zcheck_coords]