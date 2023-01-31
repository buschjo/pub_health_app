import datetime
import traceback
from collections.abc import MutableSequence
from decimal import Decimal
from io import BytesIO
from types import SimpleNamespace

import numpy as np
import osmnx as ox
import pandas as pd
import taxicab as tc
from django.utils import timezone
from shapely import to_geojson, LineString, MultiLineString, ops

from ..models import EmergencyVehicle, Emergency, RouteRecommendation

ox.config(use_cache=True, log_console=True)

import matplotlib.pyplot as plt

import matplotlib

matplotlib.use('Agg')

import requests
import json


class Router:
    tomtom_keys = ["TxzsvilHqlx0nq8nhpvPl0dOZr0MbUZS", "wGJ3eAB62RXeIvRAl72BPnypNZtxvOBf",
                   "96o6iQGlGE0zxe2M2gwjQ15hlqfhmhsR", "0WNfKPiMCQxvW9aLJylePtrkGPl4PwTU",
                   "Aw8RSGKN2jmHh3HVi6APgTmlu6SZVwAG", "DcUnnhbjYjbR4fd4c0bUBYUz5PYa9Ttb",
                   "HaUwLXM2aimAfutceDmG1iGXDPzhDyxx"]

    #WEIGHT = "travel_time"
    WEIGHT = "travelTimeInSeconds"

    graph = None
    edges = None
    nodes = None

    def __init__(self):
        self.graph = self.create_graph("Berlin Lichtenberg", 800, "drive")
        self.graph = ox.add_edge_speeds(self.graph)  # Impute
        self.graph = ox.add_edge_travel_times(self.graph)  # Travel time
        self.nodes, self.edges = ox.graph_to_gdfs(self.graph, nodes=True, edges=True)
        self.remove_oneway_restriction()
        self.add_live_data_to_graph()
        # generate Map
        self.get_map()

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
        self.edges.set_index(["u", "v", "key"], inplace=True)
        self.graph = ox.graph_from_gdfs(self.nodes, self.edges)
	
		
    def remove_oneway_restriction(self):
        self.edges["oneway"] = False
        print("One Way streets turned off")


    def get_map(self):
        ec = ox.plot.get_edge_colors_by_attr(self.graph, attr="trafficDelayInSeconds", cmap="RdYlGn_r")
        #ec = ox.plot.get_edge_colors_by_attr(self.graph, attr="length", cmap="RdYlGn_r")
        return ox.plot_graph(
            self.graph, show=False, save=False, close=False, edge_color=ec, node_color="gray",
            edge_linewidth=3
        )

    def get_recommended_vehicle_for_emergency(self, emergency: Emergency, save=True):
        emergency_vehicles: MutableSequence[EmergencyVehicle] = EmergencyVehicle.objects.filter(
            last_ping__gte=(timezone.now() - datetime.timedelta(minutes=30)), currently_dispatch=False)

        shortest_route = None

        for emergency_vehicle in emergency_vehicles:
            # Calculate the shortest path
            route = tc.shortest_path(self.graph, (float(emergency_vehicle.lat), float(emergency_vehicle.long)),
                                     (float(emergency.lat), float(emergency.long)), weight=self.WEIGHT)
            if shortest_route is None or route[4] < shortest_route.weight:
                shortest_route = RouteRecommendation(vehicle=emergency_vehicle, emergency=emergency,
                                                     nodes=route[1], start_linestring=to_geojson(route[2]),
                                                     end_linestring=to_geojson(route[3]), weight=route[4],
                                                     length=route[0])
        if shortest_route is None:
            shortest_route = RouteRecommendation(emergency=emergency)
            if save:
                shortest_route.save()
            return shortest_route
        shortest_route.route_geo_json = self.get_route_as_geojson(shortest_route)
        if save:
            shortest_route.save()
        return shortest_route

    def update_map(self) -> bytes:
        fig, ax = self.get_map()
        fig, ax = self.update_emergency_vehicles(fig, ax)
        fig, ax = self.update_emergencies(fig, ax)

        plt.box(False)
        plt.axis('off')

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0)

        plt.close(fig)
        fig.clf()

        return buf.getvalue()

    def update_emergency_vehicles(self, fig, ax):
        emergency_vehicles: MutableSequence[EmergencyVehicle] = EmergencyVehicle.objects.filter(
            last_ping__gte=(timezone.now() - datetime.timedelta(minutes=30)))
        for emergency_vehicle in emergency_vehicles:
            color = None
            if emergency_vehicle.currently_dispatch:
                color = 'blue'
            else:
                color = '#7F00FF'
            ax.scatter(emergency_vehicle.long, emergency_vehicle.lat, c=color, s=100)
            ax.text(
                emergency_vehicle.long - Decimal(0.00013), emergency_vehicle.lat - Decimal(0.00013),
                f"{emergency_vehicle.call_name}\nLast ping: {emergency_vehicle.last_ping.strftime('%H:%M:%S')}",
                ha="right", va="top", fontsize=8, bbox=dict(alpha=0.7, boxstyle="round,pad=0.3"))
        return fig, ax

    def update_emergencies(self, fig, ax):
        emergencies: MutableSequence[Emergency] = Emergency.objects.filter(
            resolved=False)
        for emergency in emergencies:
            ax.scatter(emergency.long, emergency.lat, c='red', s=100)
            ax.text(
                emergency.long - Decimal(0.00013), emergency.lat - Decimal(0.00013),
                f"{emergency.type}\nHappened: {emergency.timestamp.strftime('%H:%M:%S')}\nDispatched: {(emergency.dispatched_vehicle or SimpleNamespace(call_name='False')).call_name}",
                ha="right", va="top", fontsize=8, bbox=dict(facecolor='red', alpha=0.7, boxstyle="round,pad=0.3"))
        return fig, ax

    def create_map_from_recommended_route(self, route: RouteRecommendation):
        '''
        Create a binary string containing the map with the given route
        :param route: array of node ids forming the route
        :return: binary of image
        '''
        fig, ax = self.get_map()
        fig, ax = tc.plot_graph_route(self.graph, route.get_tc_tupel(), route_linewidth=6, node_size=0, bgcolor='k',
                                      show=False,
                                      save=False, close=False, ax=ax, route_color='red', route_alpha=0.8)
        self.update_emergency_vehicles(fig, ax)
        self.update_emergencies(fig, ax)

        plt.box(False)
        plt.axis('off')

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0)

        plt.close(fig)
        fig.clf()

        return buf.getvalue()

    def dispatch_to_recommended_route(self, route: RouteRecommendation):
        geo_json = self.get_route_as_geojson(route)
        print(geo_json)
        # Call Vehicle endpoint
        route.vehicle.currently_dispatch = True
        route.vehicle.save()
        route.emergency.dispatched_vehicle = route.vehicle
        route.emergency.save()
        pass

    def get_route_as_geojson(self, route: RouteRecommendation):
        linestrings = []
        if route.get_start_linestring():
            linestrings.append(route.get_start_linestring())
        for u, v in zip(route.nodes[:-1], route.nodes[1:]):
            data = min(self.graph.get_edge_data(u, v).values(), key=lambda d: d[self.WEIGHT])
            if "geometry" in data:
                linestrings.append(data["geometry"])
            else:
                linestrings.append(LineString([(self.graph.nodes[u]["x"], self.graph.nodes[u]["y"]),
                                               (self.graph.nodes[v]["x"], self.graph.nodes[v]["y"])]))
        if route.get_end_linestring():
            linestrings.append(route.get_end_linestring())
        print(linestrings)
        multi_line_string = MultiLineString(linestrings)
        return to_geojson(ops.linemerge(multi_line_string))

    def resolve_emergency(self, emergency: Emergency):
        emergency.resolved = True
        emergency.dispatched_vehicle.currently_dispatch = False
        emergency.save()
        emergency.dispatched_vehicle.save()
