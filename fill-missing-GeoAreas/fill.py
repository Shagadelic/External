import pandas as pd
import geopandas as gpd
import libpysal
import networkx as nx
from collections import deque

from pathlib import Path

geography = pd.read_csv(
    Path(__file__).parent.parent / "area_coordinates.csv"
).set_index("area")


# Index of multiple deprivation
#superarea -> lsoa

# Add a super areas column
output_area_df = pd.DataFrame(geography.reset_index()["area"], columns=["area"])
output_area_df["lsoa"] = output_area_df["area"].str[:6]

# loads the gisd data, adds the rank column,
# renames the column "Kreiskennziffer" to "lsoa" for joining tables later and reformats the superarea/lsoa code.
gisd_df = pd.read_csv(
   Path(__file__).resolve().parent /  "Kreis_2014.csv",
    encoding="latin1",
    usecols=["Kreiskennziffer", "GISD_Score", "GISD_10"],
    dtype={"Kreiskennziffer": str, "GISD_Score": float, "GISD_10": int},
)
gisd_df.rename(columns={"Kreiskennziffer": "lsoa"}, inplace=True)
gisd_df["lsoa"] = gisd_df["lsoa"].map(lambda x: "D{:0>5}".format(x))

# gets the superareas missing from either the gisd_df or the geography/output_area_df
geo_gisd_sa_dif_df = pd.DataFrame(
    set(gisd_df.lsoa).symmetric_difference(output_area_df.lsoa), columns=["lsoa"]
).sort_values(by="lsoa")

# gets the areas from geography not in gisd
geosupar_not_in_gisd_df = geo_gisd_sa_dif_df[
    geo_gisd_sa_dif_df["lsoa"].isin(output_area_df.lsoa)
].sort_values(by="lsoa")

## Gets geographic neighbours (gisd) of the missing areas and assigns them an averaged value

# gets geometry file
ger_geometry = gpd.read_file(
    Path(__file__).resolve().parent / "geometry/areas.shp"
)


# computes polygons of superareas
geometry_superareas = gpd.GeoDataFrame(
    ger_geometry.dissolve(by="super_area"), columns=["geometry"]
).reset_index()

# gets geometry of, from the GISD-file missing superareas
missing_geom_ar = geometry_superareas[
    geometry_superareas["super_area"].isin(geosupar_not_in_gisd_df["lsoa"])
]

# computes the polygon neighbours
superarea_weights = libpysal.weights.Queen.from_dataframe(geometry_superareas)
# normalizes weights for the areas
superarea_weights.transform = "r"

# gets neighbours of the missing superareas
miss_idx = (missing_geom_ar.index.tolist(), missing_geom_ar.super_area.tolist())

nodes = [
    (miss_idx[0][i], {"super_area": miss_idx[1][i], "GISD_Score": 0})
    for i in range(len(miss_idx[0]))
]
edges = [
    (miss_idx[0][i], j[0], {"weight": j[1]})
    for i in range(len(miss_idx[0]))
    for j in superarea_weights[miss_idx[0][i]].items()
]

# creates a graph
void = nx.DiGraph(contained=miss_idx[0])
# adds nodes
void.add_nodes_from(nodes)
# adds edges
void.add_edges_from(edges)

# intitializes the successors of nodes for the score udates
for node in void.nodes():
    void.nodes[node]["checked_neighbours"] = {j: 0 for j in void.neighbors(node)}

# get nodeIds for the nodes from GISD, without an outgoing edge
outsiderLi = list(set(void.graph["contained"]).symmetric_difference(void.nodes()))

# Initialzes outer nodes from edges correctly
for outer_node in outsiderLi:
    void.nodes[outer_node]["super_area"] = geometry_superareas.at[
        outer_node, "super_area"
    ]
    void.nodes[outer_node]["GISD_Score"] = gisd_df.loc[
        gisd_df.lsoa == void.nodes[outer_node]["super_area"], "GISD_Score"
    ].values[0]

# put them into a queue
node_score = deque(outsiderLi)

while node_score:
    # update values of the predeccessors -> put updated nodes into the queue if not all neighbours contributed to the final-GISD score
    cur_id = node_score.pop()
    current_node = void.nodes[cur_id]

    gisd = current_node["GISD_Score"]
    if gisd:
        score = gisd
    else:
        score = sum(current_node["Neigh_score"].values()) / len(
            current_node["Neigh_score"].values()
        )
    predecessors = void.predecessors(cur_id)
    # pass current value to pred. and insert it into its neighbourhood score dict if it is not there yet
    for pred in predecessors:
        if not void.nodes[pred]["GISD_Score"]:
            if "Neigh_score" not in void.nodes[pred]:
                void.nodes[pred]["Neigh_score"] = {}
            if cur_id not in void.nodes[pred]["Neigh_score"].keys():
                void.nodes[pred]["Neigh_score"].update({cur_id: score})
                void.nodes[pred]["checked_neighbours"][cur_id] = 1
            if pred in node_score:
                # if a predecessor has been placed in the queue beforehand and is encountered again,
                # push it back once more and remove the first occurence.
                node_score.remove(pred)
            node_score.appendleft(pred)
    # if the score is not final, check if it has been computed, otherwise put it back into the queue
    if not gisd:
        if len(current_node["Neigh_score"]) == sum(
            current_node["checked_neighbours"].values()
        ):
            current_node["GISD_Score"] = score
        else:
            node_score.appendleft(cur_id)

# gets superarea/lsoa codes and the gisd_score and creates a dataframe
miss_sup = {"lsoa": [], "GISD_Score": []}
for node in void.graph["contained"]:
    miss_sup["lsoa"].append(void.nodes[node]["super_area"])
    miss_sup["GISD_Score"].append(void.nodes[node]["GISD_Score"])

sup_areas_to_add = pd.DataFrame(miss_sup, columns=["lsoa", "GISD_Score"])

# concatenates gisd table with the new superareas
gisd_df = pd.concat([gisd_df, sup_areas_to_add], axis=0)
gisd_df.reset_index(drop=True, inplace=True)

gisd_df["iomd_rank"] = gisd_df["GISD_Score"].rank(method="min").astype(int)
gisd_df["GISD_10"] = pd.qcut(gisd_df.iomd_rank, 10, labels=False) + 1

iomd_df = output_area_df.merge(gisd_df, how="left", on="lsoa")
# renames columns to fit the JUNE framework
iomd_df.rename(columns={"area": "output_area", "GISD_10": "iomd_decile"}, inplace=True)

# writes table to .csv file
table_cols = ["output_area", "lsoa", "iomd_rank", "iomd_decile"]
iomd_df.to_csv(
    Path(__file__).resolve().parent / "index_of_multiple_deprivation.csv",
    columns=table_cols,
    index=False,
)
