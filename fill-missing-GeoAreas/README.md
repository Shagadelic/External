An algorithm that is used to assign an index of multiple deprivation value to areas from area_coordinates.csv not in the Kreis_2014.csv data.  
Or in other words fill a hole of areas with missing values by the usage of available values from the surrounding neighbours.
It uses a deque to make sure that values of the hubs are set before influencing missing value areas with fewer neighbours.
Neighbourhood relations are processed with the help of networkx.
