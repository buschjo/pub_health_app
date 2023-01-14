import traceback

import numpy as np
import osmnx as ox
import pandas as pd

ox.config(use_cache=True, log_console=True)

import requests
import json


class Router:
    tomtom_keys = ["TxzsvilHqlx0nq8nhpvPl0dOZr0MbUZS", "wGJ3eAB62RXeIvRAl72BPnypNZtxvOBf",
                   "96o6iQGlGE0zxe2M2gwjQ15hlqfhmhsR", "0WNfKPiMCQxvW9aLJylePtrkGPl4PwTU",
                   "Aw8RSGKN2jmHh3HVi6APgTmlu6SZVwAG", "DcUnnhbjYjbR4fd4c0bUBYUz5PYa9Ttb",
                   "HaUwLXM2aimAfutceDmG1iGXDPzhDyxx"]
    graph = None
    edges = None
    nodes = None

    def __init__(self):
        self.graph = self.create_graph("Berlin Alexanderplatz", 500, "drive")
        self.nodes, self.edges = ox.graph_to_gdfs(self.graph, nodes=True, edges=True)
        self.add_live_data_to_graph()
        # generate Map
        ec = ox.plot.get_edge_colors_by_attr(self.graph, attr="trafficDelayInSeconds", cmap="RdYlGn_r")
        fig, ax = ox.plot_graph(
            self.graph, show=True, save=True, filepath="graph.png", edge_color=ec, edge_linewidth=3
        )

    def create_graph(self, loc, dist, transport_mode, loc_type="address"):
        """
        Method to create a graph based on open streets maps
        :param loc: location of the map
        :param dist: size of graph
        :param transport_mode: Mode of travel ( ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’, ‘none’ )
        :param loc_type: defines type of the loc variable (address or points), by default address
        :return: Generated graph
        """
        g = None
        if loc_type == "address":
            g = ox.graph_from_address(loc, dist=dist, network_type=transport_mode)
        elif loc_type == "points":
            g = ox.graph_from_point(loc, dist=dist, network_type=transport_mode)
        return g

    def get_live_data(self, edge, idx):
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{edge['u_y'].iloc[1]},{edge['u_x'].iloc[1]}:{edge['v_y'].iloc[1]},{edge['v_x'].iloc[1]}/json?sectionType=traffic&report=effectiveSettings&routeType=eco&traffic=true&avoid=unpavedRoads&travelMode=car&key={self.tomtom_keys[idx % len(self.tomtom_keys)]}"
        response = requests.request("GET", url)
        if response.status_code != 200:
            raise response.raise_for_status()
        response_object = json.loads(response.text)
        route = pd.json_normalize(response_object['routes'])
        return route

    def get_nodes_with_coordinates(self):
        self.nodes.reset_index(inplace=True)
        return self.nodes[['osmid', 'y', 'x']].copy()

    def map_coordinates_to_edge(self, node_name, edges, nodes):
        df = pd.merge(edges, nodes, left_on=node_name, right_on='osmid')
        df.drop(['osmid_y'], axis=1, inplace=True)
        df.rename(columns={"y": f"{node_name}_y", "x": f"{node_name}_x", 'osmid_x': 'osmid'}, inplace=True)
        return df

    def add_live_data_to_graph(self):
        # prepare edges
        self.edges.reset_index(inplace=True)
        self.edges["u_x"] = np.nan
        self.edges["u_y"] = np.nan
        self.edges["v_x"] = np.nan
        self.edges["v_y"] = np.nan
        self.edges["trafficDelayInSeconds"] = np.nan
        self.edges["travelTimeInSeconds"] = np.nan
        self.edges["trafficLengthInMeters"] = np.nan

        # Fill edges with coordinates
        short_nodes_df = self.get_nodes_with_coordinates()
        self.edges = self.map_coordinates_to_edge('u', self.edges, short_nodes_df)
        self.edges = self.map_coordinates_to_edge('v', self.edges, short_nodes_df)

        # Fill edges with live traffic data
        for (idx, row) in self.edges.iterrows():
            try:
                traffic_route = self.get_live_data(self.edges.iloc[idx], idx)
                self.edges.at[idx, "trafficDelayInSeconds"] = traffic_route["summary.trafficDelayInSeconds"].iloc[0]
                self.edges.at[idx, "travelTimeInSeconds"] = traffic_route["summary.travelTimeInSeconds"].iloc[0]
                self.edges.at[idx, "trafficLengthInMeters"] = traffic_route["summary.trafficLengthInMeters"].iloc[0]
            except requests.exceptions.HTTPError as err:
                print(f"HTTP-Error while querying TomTom - are the keys expired? - {err}")
                print(traceback.format_exc())
            except Exception as e:
                print(f"Unknown-Error while querying TomTom - {e}")
                print(traceback.format_exc())

        # update graph
        self.nodes.set_index("osmid", inplace=True)
        self.edges.set_index(["u","v","key"], inplace=True)
        self.graph = ox.graph_from_gdfs(self.nodes, self.edges)

    def print_edges_with_zero_traffic(self):
        street = self.edges[self.edges.speed == 0]
        for (idx, row) in street.iterrows():
            print(f"{row.loc['u_y']},{row.loc['u_x']},red,marker")
