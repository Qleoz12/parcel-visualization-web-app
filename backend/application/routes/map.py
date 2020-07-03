from fastapi import APIRouter, Depends
from geojson import Feature, FeatureCollection, Point
import openrouteservice
import pandas
from typing import List, Optional
import json
import copy
import collections

from application.models.Depot import Depot
from application.models.Delivery import Delivery
from application.models.Route import ORSResult
from application.models.Vehicle import Vehicle
from application.models.Scenario import Scenario

from application.config import Settings

from application.dependencies.data_dependencies import deliveries_param, vehicles_param, scenario_param

settings = Settings(_env_file='./application/.env')

router = APIRouter()


@router.post("/geojson", response_model=ORSResult)
def get_geojson(algorithm: int, deliveries: Optional[List[Delivery]] = Depends(deliveries_param),
                vehicles: Optional[List[Vehicle]] = Depends(vehicles_param),
                scenario: Optional[Scenario] = Depends(scenario_param)):
    """
    Loads the dummy depot, vehicle and delivery data, and optimizes routes based on that.
    If no deliveries or vehicles are specified, they are loaded from file.
    :param algorithm: the algorithm specifier of the algorithm that should be used.
    :param deliveries: an optional list of deliveries to use for the routes.
    :param vehicles: an optional list of vehicles to use to do the deliveries.
    :param scenario: an optional object containing information about a scenario.
    :return: an object containing the GeoJSON that can be visualised, and the routes.
    """
    if algorithm == 0:
        # ORS optimization
        depots = load_depots('./application/assets/depots.csv')
        ors = ors_request(deliveries, vehicles, depots)
        return {
            'geojson': make_ors_geojson(ors, vehicles, depots)
        }
    elif algorithm == 1:
        # Almende algorithm
        almende = almende_request(scenario)
        almende_geojson = make_almende_geojson(almende)
        return {
            'geojson': almende_geojson
        }


def load_depots(csv_path: str) -> List[Depot]:
    """
    Parses the csv file to a list of depot models.
    :param csv_path: the csv file to be parsed
    :return: List of depot models
    """
    depots_data = pandas.read_csv(
        csv_path,
        index_col="ID"
    )
    deps = []
    for depot in depots_data.itertuples():
        deps.append(Depot.from_csv_tuple(depot))
    return deps


def ors_request(delv: List[Delivery], v: List[Vehicle], dep: List[Depot]):
    """
    Converts the three lists of models to ORS specific classes and optimizes routes using those.
    :param delv: A list of deliveries that need to be modeled.
    :param v: A list of vehicles that need to be modeled.
    :param dep: A list of depots that need to be modeled
    :return: An ORS optimization object containing the calculated optimized route.
    """
    ors_client = openrouteservice.Client(
        key=settings.ORS_API_KEY)  # Get an API key from https://openrouteservice.org/dev/#/signup
    ors_jobs = []
    ors_vehicles = []
    for delivery in delv:
        ors_jobs.append(openrouteservice.optimization.Job(
            id=delivery.id,
            location=[delivery.longitude, delivery.latitude],
            amount=[delivery.needed_amt]
        ))
    for vehicle in v:
        start_dep: Depot = dep[vehicle.depot - 1]
        end_dep: Depot = dep[vehicle.depot - 1]
        ors_vehicles.append(openrouteservice.optimization.Vehicle(
            id=vehicle.id,
            start=[start_dep.longitude, start_dep.latitude],
            end=[end_dep.longitude, end_dep.latitude],
            capacity=[vehicle.capacity]
        ))
    ors_optimization = ors_client.optimization(
        jobs=ors_jobs,
        vehicles=ors_vehicles,
        geometry=True
    )
    return ors_optimization


def get_ors_route(num, geometry, dur, dist):
    """
    Constructs the feature for the openrouteservice route object.
    :param num: The numeric identifier of the route.
    :param geometry: The geometry of the route.
    :param dur: The total duration of the route in seconds.
    :param dist: The distance of the route in metres.
    :return: A Feature object containing the GeoJSON for a route.
    """
    decoded = openrouteservice.convert.decode_polyline(geometry)  # Route geometry is encoded
    h, m = divmod(round(dur / 60), 60)
    return Feature(geometry=decoded, properties={
        "type": "route",
        "name": "Route",
        "number": num,
        "title": "Route " + str(num),
        "distance": round(dist, 1),
        "duration_h": h,
        "duration_m": m,
        "cost": 0,
        "idle_time": 0
    })


def get_ors_delivery(num, delivery, history):
    """
    Constructs the feature for the openrouteservice delivery object.
    :param num: The numeric identifier of the route.
    :param delivery: The delivery object to turn into a feature.
    :param history: The past locations of this delivery.
    :return: A Feature object containing the GeoJSON for a delivery.
    """
    h, m = divmod(round(delivery['arrival'] / 60), 60)
    dist, geom, segments = ors_directions(history)
    return Feature(geometry=Point((delivery['location'])), properties={
        "type": "delivery",
        "name": "Delivery",
        "number": delivery['job'],
        "title": "Delivery " + str(delivery['job']),
        "route_number": num,
        "arrival_h": h,
        "arrival_m": m,
        "distance": round(delivery['distance'], 1),
        "vehicle": num,
        "duration": 1,
        "parcels": [delivery['job']],
        "toDepot": False,
        "arrival_mode": "Manual",
        "single_route": Feature(geometry={"type": "LineString", "coordinates": geom}, properties={
            "type": "single_route",
            "name": "Route",
            "number": delivery['job'],
            "title": "Route for delivery "+str(delivery['job'],),
            "distance": dist,
            "duration_h": h,
            "duration_m": m
        })
    })


def get_ors_start_stop(num, event):
    """
    Constructs the feature for the openrouteservice start/stop object.
    :param num: The numeric identifier of the route.
    :param event: The start or stop object to turn into a feature.
    :return: A Feature object containing the GeoJSON for a start or stop event.
    """
    h, m = divmod(round(event['arrival'] / 60), 60)
    return Feature(geometry=Point((event['location'])), properties={
        "type": event['type'],
        "number": 0,
        "arrival_h": h,
        "arrival_m": m,
        "distance": round(event['distance'], 1),
        "duration": 0,
        "arrival_mode": "Manual",
        "vehicle": num
    })


def get_ors_depot(depot, index, routes, parcels):
    """
    Constructs the feature for the openrouteservice depot object.
    :param depot: The depot object to turn into a feature.
    :param index: The identifier of the depot.
    :param routes: The routes that interact with the depot.
    :param parcels: The list of parcels present at the depot.
    :return: A Feature object containing the GeoJSON for a delivery.
    """
    return Feature(geometry=Point(([depot.longitude, depot.latitude])), properties={
        "type": "depot",
        "name": "Depot",
        "number": index + 1,
        "title": "Depot " + str(index + 1),
        "route_numbers": routes,
        'parcels': parcels
    })


def make_ors_geojson(openrs, vs: List[Vehicle], deps: List[Depot]) -> FeatureCollection:
    """
    Constructs JSON in the GeoJSON format using the calculated ORS routes and the depots.
    :param openrs: An ORS optimization object that has calculated routes.
    :param deps: A list of depot models to include in the GeoJSON.
    :param vs: A list of vehicle models to include in the GeoJSON.
    :return: A FeatureCollection object containing the GeoJSON for the visualisation.
    """
    depot_routes = [[] for x in range(len(deps))]
    depot_parcels = [[] for x in range(len(deps))]
    features = []
    enumerator = 1
    for route in openrs['routes']:
        past_deliveries = []
        features.append(get_ors_route(enumerator, route["geometry"], route["duration"], route["distance"]))
        depot_routes[vs[route['vehicle'] - 1].depot - 1].append(enumerator)
        for delivery in route['steps']:
            if delivery['type'] == 'job':
                past_deliveries.append(delivery['location'])
                depot_parcels[vs[route['vehicle'] - 1].depot - 1].append(delivery["job"])
                features.append(get_ors_delivery(enumerator, delivery, past_deliveries))
            elif delivery['type'] == 'start' or delivery['type'] == 'end':
                past_deliveries.append(delivery['location'])
                features.append(get_ors_start_stop(enumerator, delivery))
        enumerator += 1

    for depot in deps:
        features.append(get_ors_depot(depot, deps.index(depot), depot_routes[deps.index(depot)],
                                      depot_parcels[deps.index(depot)]))
    return FeatureCollection(features)


def almende_request(scenario):
    """"
    Performs a request to the almende routing algorithm with the given input scenario file.
    :param scenario: An object containing the input variables that form the scenario.
    :return: A JSON object with the by Almende calculated routes.
    """
    file_location = scenario.write_to_file()
    # TODO: make request to Almendes algorithm with the computed file location (or scenario object).

    # For now we shall use a sample json output file to return.
    with open('./application/assets/delayed_output.json', 'r') as f:
        data = json.load(f)
    return data


def ors_directions(coordinate_list):
    """"
    Performs a request to ORS to compute the route coordinates between coordinates defined by the Almende algorithm.
    :param coordinate_list: A list of coordinates between which to calculate a route.
    :return: The distance of the route, the coordinate information of the route, and the information of stopovers.
    """
    if settings.ORS_URL != "":
        ors_client = openrouteservice.Client(base_url=settings.ORS_URL)
    else:
        ors_client = openrouteservice.Client(
            key=settings.ORS_API_KEY)  # Get an API key from https://openrouteservice.org/dev/#/signup

    ors_dirs = ors_client.directions(coordinate_list, profile='driving-car')
    geometry = openrouteservice.convert.decode_polyline(ors_dirs["routes"][0]["geometry"])["coordinates"]
    return ors_dirs["routes"][0]["summary"]["distance"], geometry, ors_dirs["routes"][0]["segments"]


def make_almende_geojson(almende_data):
    """
    Constructs JSON in the GeoJSON format according to the Almende algorithm using the given input scenario file.
    :param almende_data: A JSON object containing the computed routes in Almendes output format.
    :return: A FeatureCollection object containing the GeoJSON for the visualisation.
    """
    features = []
    enumerator = 1
    depots = get_depot_list(almende_data["nodes"])
    counter = 499
    for vehicle in almende_data['vehicles']:
        coordinate_list, route_features, idle_time, counter, depots = iterate_actions(enumerator, depots, vehicle,
                                                                                      almende_data, counter)
        distance, geom, segments = ors_directions(coordinate_list)
        geometry = {"type": "LineString", "coordinates": geom}
        h, m = divmod(len(vehicle["actions"]), 60)
        metrics = (almende_data["totalcost"]/len(almende_data["vehicles"]), round(distance, 1), idle_time, h, m,
                   enumerator)
        features += append_route(add_distances(route_features, segments), geometry, metrics)
        enumerator += 1
    features += depots
    features = compute_single_routes(add_handovers_to_deliveries(features), almende_data["nodes"])
    return FeatureCollection(features)


def iterate_actions(enumerator, depots, vehicle, almende_data, counter):
    """
    Iterates over the actions that a vehicle undertakes on its route and converts them to features for the GeoJSON.
    :param enumerator: A number that identifies the route/vehicle number.
    :param depots: A list of all depots available in the scenario.
    :param vehicle: The current vehicle object with actions to iterate over.
    :param almende_data: The complete Almende algorithm output data.
    :param counter: A number that serves as a unique key for handovers.
    :return: A list of coordinates, all actions translated to features, the total idle time, a handover key counter and
    an updated list of depots.
    """
    ActionFactory = collections.namedtuple('ActionFactory', 'num action nodes vehicle minute requests location')
    idle_time = cur_action = 0
    prev_from = prev_to = delayed_prev_from = delayed_prev_to = -1
    coordinate_list, route_features, past_waypoints = ([] for i in range(3))
    route_features.append(get_start(almende_data["nodes"], vehicle, enumerator))
    action_list = make_flat_action_list(vehicle["actions"])
    for i in range(0, len(action_list)):
        action = action_list[i]
        cur_action = ActionFactory(enumerator, action, almende_data["nodes"], vehicle, action["minute"], almende_data["requests"],
                                   get_location(almende_data["nodes"], get_nearest_node(vehicle, action["minute"])))
        if action["actionType"] == "PICKUP":
            depots[get_depot_index(depots, get_nearest_node(vehicle, i))].properties["route_numbers"].append(enumerator)
            route_features, past_waypoints = add_pickup(cur_action, route_features, past_waypoints)
        elif action["actionType"] == "HANDOVER":
            route_features, past_waypoints = add_handover(cur_action, counter, past_waypoints, route_features)
            counter += 1
        elif action["actionType"] == "DELIVER":
            for delivery in action["relatedRequests"]:
                route_features, past_waypoints = add_delivery(cur_action, delivery, past_waypoints, route_features,
                                                              check_for_depot(almende_data["nodes"], get_nearest_node(vehicle, i)))
        elif action["actionType"] == "DELAYED" and (action["from"] != delayed_prev_from or action["to"] != delayed_prev_to):
            idle_time += action["duration"]
            route_features.append(get_delayed(cur_action))
            delayed_prev_from = action["from"]
            delayed_prev_to = action["to"]
        elif action["actionType"] == "MODE_CHANGE":
            route_features.append(get_mode_change(cur_action))
        elif action["actionType"] == "TRAVELLING" and (action["from"] != prev_from or action["to"] != prev_to):
            if action["from"] == action["to"]:
                idle_time += action["duration"]
                route_features.append(get_delayed(cur_action))
            else:
                coordinate_list = append_coords(coordinate_list, almende_data["nodes"], action["from"], action["to"])
            prev_from = action["from"]
            prev_to = action["to"]
    route_features.append(get_end(enumerator, cur_action.minute, almende_data["nodes"], vehicle))
    return coordinate_list, route_features, idle_time, counter, depots


def get_end(num, minute, nodes, vehicle):
    location = get_location(nodes, get_last_node(vehicle, minute))
    h, m, n, a = get_init_values(minute, [])
    return Feature(geometry=Point(location), properties={
        "type": "end",
        "number": 0,
        "arrival_h": h,
        "arrival_m": m,
        "distance": 0,
        "duration": 0,
        "arrival_mode": get_prev_mode(vehicle, minute),
        "vehicle": num
    })


def append_coords(list, nodes, from_c, to_c):
    """
    Appends coordinates to the list of coordinates.
    :param list: The current list of coordinates.
    :param nodes: All nodes in the scenario.
    :param from_c: The node number from which the route segment starts.
    :param to_c: The node number to which the route segment leads.
    :return: The updated list of coordinates.
    """
    if len(list) > 0:
        list.pop()
    list.append(get_location(nodes, from_c))
    list.append(get_location(nodes, to_c))
    return list


def make_flat_action_list(actions):
    """
    Takes the list of actions and reduces it to a flat list.
    :param actions: The list of actions.
    :return: The flat list of actions.
    """
    res = []
    for i in range(0, len(actions)):
        res += make_list(actions, i)
    return res


def make_list(actions, i):
    """
    Creates a list of the actions performed at a location in time, to provide support for the instances where multiple
    actions are executed simultaneously.
    :param actions: The list of actions of a route.
    :param i: The minute for which to make a list of actions
    :return: A list of one or more actions that occur at the given minute.
    """
    action_list = actions[str(i)]
    if type(action_list) != list:
        action_list = [action_list]
    for action in action_list:
        action["minute"] = i
    return action_list


def append_route(features, geometry, metrics):
    """
    Appends a route feature to the list of features.
    :param features: The current list of features.
    :param geometry: The geometry information of the route.
    :param metrics: A tuple of aggregated values that describe the route.
    :return: The list of features appended with a route feature.
    """
    properties = {
        "type": "route",
        "name": "Route",
        "number": metrics[5],
        "title": "Route " + str(metrics[5]),
        "distance": metrics[1],
        "duration_h": metrics[3],
        "duration_m": metrics[4],
        "idle_time": metrics[2],
        "cost": metrics[0]
    }
    features.append(Feature(geometry=geometry, properties=properties))
    return features


def add_handovers_to_deliveries(features):
    """
    Adds the handover locations of a delivery to its handovers property.
    :param features: A FeatureCollection containing all features of a route.
    :return: A FeatureCollection with updated delivery handover properties.
    """
    handovers = [ft for ft in features if ft.properties["type"] == "handover"]
    for ft in features:
        if ft.properties["type"] == "delivery":
            for ho in handovers:
                if ft.properties["number"] in ho.properties["involved"]:
                    ft.properties["handovers"].append(ho.geometry)
    return features


def compute_single_routes(features, nodes):
    for ft in features:
        if ft.properties["type"] == "delivery":
            coordinate_list = [get_location(nodes, ft.properties["origin"])]
            coordinate_list += ft.properties["waypoints"]
            coordinate_list.append(ft.geometry["coordinates"])
            dist, geom, seg = ors_directions(coordinate_list)
            ft.properties["single_route"] = Feature(geometry={"type": "LineString", "coordinates": geom}, properties={
                "type": "single_route",
                "name": "Route",
                "number": ft.properties["number"],
                "title": "Route for delivery "+str(ft.properties["number"]),
                "distance": dist,
                "duration_h": ft.properties["arrival_h"],
                "duration_m": ft.properties["arrival_m"]
            })
    return features


def add_distances(features, segments):
    """
    Adds the intermediate distance values to features.
    :param features: A FeatureCollection containing all features of a route.
    :param segments: A list containing information about stopovers, including their distances coverd from origin.
    :return: A FeatureCollection with updated feature distances.
    """
    prev = features[0].geometry
    ind = dist = 0
    for ft in features:
        if ft.geometry != prev:
            while "distance" not in segments[ind]:
                ind += 1
            dist += segments[ind]["distance"]
            prev = ft.geometry
            ind += 1
        ft.properties["distance"] = dist
    return features


def get_depot_list(nodes):
    """
    Creates a list of depots from nodes.
    :param nodes: The total available nodes that could be depots.
    :return: A list of depot features.
    """
    res = []
    for point in nodes:
        # a node is a depot if its initial storage contains parcels.
        init_storage = point["storage"]["0"]
        if len(init_storage) > 0:
            res.append(get_depot(point["coordinates"], point["id"], init_storage))
    return res


def get_depot(coordinates, id, parcels):
    """
    Creates a depot feature.
    :param coordinates: The location of the depot.
    :param id: The identifier of the depot.
    :param parcels: The list of parcels present at the depot.
    :return: A depot feature object.
    """
    return Feature(geometry=Point(([coordinates["longitude"], coordinates["latitude"]])),
                   properties={
                       "type": "depot",
                       "name": "Depot",
                       "number": id,
                       "title": "Depot " + str(id),
                       "route_numbers": [],
                       "parcels": parcels
                   })


def get_start(nodes, vehicle, num):
    """
    Creates a start feature.
    :param nodes: A list of available nodes in the route.
    :param vehicle: The vehicle object of which to find the start.
    :param num: The identifier of the vehicle/route.
    :param load: The current load of the vehicle.
    :return: A start feature object.
    """
    current_mode = vehicle["mode"]["0"]
    start_loc = get_location(nodes, [vehicle["actions"]["0"]][0]["from"])
    feature = Feature(geometry=Point(start_loc), properties={
            "type": "start",
            "name": "Start",
            "title": "Starting point",
            "number": 0,
            "arrival_h": 0,
            "arrival_m": 0,
            "distance": 0,
            "vehicle": num,
            "mode": current_mode
        })
    return feature


def add_pickup(action, features, waypoints):
    """
    Creates a pickup feature.
    :param action: All the information about the action object of the pickup.
    :param features: The list of features for the current route.
    :param waypoints: The list of past waypoints.
    :return: A pickup feature object.
    """
    h, m, parcels, parcel_str = get_init_values(action.minute, action.action["relatedRequests"])
    feature = Feature(geometry=Point(action.location),
                properties={
                    "type": "pickup",
                    "name": "Pickup",
                    "parcels": parcels,
                    "title": "Pickup of parcel(s) " + parcel_str,
                    "route_number": action.num,
                    "arrival_h": h,
                    "arrival_m": m,
                    "duration": action.action["duration"],
                    "distance": 0,
                    "vehicle": action.num,
                    "arrival_mode": get_prev_mode(action.vehicle, action.minute)
                })
    features.append(feature)
    waypoints.append(feature)
    return features, waypoints


def add_handover(action, counter, waypoints, features):
    """
    Creates a handover feature.
    :param action: All the information about the action object of the handover.
    :param counter: The identifier of the handover.
    :param waypoints: The past locations of the handover.
    :param features: The list of features of the current route.
    :return: A handover feature object.
    """
    h, m, parcels, parcel_str = get_init_values(action.minute, action.action["relatedRequests"])
    feature = Feature(geometry=Point(action.location),
                properties={
                    "type": "handover",
                    "name": "Handover",
                    "total_parcels": parcels,
                    "key": counter,
                    "title": "Handover of parcel(s) " + parcel_str,
                    "route_number": action.num,
                    "arrival_h": h,
                    "arrival_m": m,
                    "duration": action.action["duration"],
                    "distance": 0,
                    "vehicle": action.num,
                    "waypoints": copy.deepcopy(waypoints),
                    "involved": [action.num],
                    "parcels": [],
                    "arrival_mode": get_prev_mode(action.vehicle, action.minute)
                })
    features.append(feature)
    waypoints.append(feature)
    return features, waypoints


def get_delivery_waypoints(waypoints, delivery):
    """
    Creates a list of points where this delivery has been, following past deliveries, handovers and pickups.
    :param waypoints: The past actions for the current vehicle.
    :param delivery: The delivery to track points for.
    :return: A list of coordinates of points the delivery has been past.
    """
    res = []
    for point in waypoints:
        res.append(point.geometry["coordinates"])
        if point.properties["type"] == "handover" and delivery in point.properties["parcels"]:
            new_wp = point.properties["waypoints"]
            new_wp.reverse()
            return res + get_delivery_waypoints(new_wp, delivery)
        elif point.properties["type"] == "pickup" and delivery in point.properties["parcels"]:
            return res
    return res


def add_delivery(action, delivery, waypoints, features, to_depot):
    """
    Creates a delivery feature.
    :param action: All the information about the action object of the delivery.
    :param delivery: The identifier of the current delivery.
    :param waypoints: The list of all past locations of this delivery.
    :param features: The list of features for the current route.
    :param to_depot: A boolean that determines if a delivery is done at a depot or not.
    :return: A delivery feature object.
    """
    wp_modified = copy.deepcopy(waypoints)
    wp_modified.reverse()
    wp = get_delivery_waypoints(wp_modified, delivery)
    wp.reverse()
    h, m = divmod(action.minute, 60)
    loc = get_location(action.nodes, get_nearest_node(action.vehicle, action.minute))
    feature = Feature(geometry=Point(loc),
                properties={
                    "type": "delivery",
                    "name": "Delivery",
                    "number": delivery,
                    "title": "Delivery " + str(delivery),
                    "route_number": action.num,
                    "arrival_h": h,
                    "arrival_m": m,
                    "duration": action.action["duration"],
                    "distance": 0,
                    "vehicle": action.num,
                    "origin": get_origin_depot(action.requests, delivery),
                    "handovers": [],
                    "parcels": [],
                    "waypoints": wp,
                    "to_depot": to_depot,
                    "single_route": Feature(),
                    "arrival_mode": get_prev_mode(action.vehicle, action.minute)
                })
    features.append(feature)
    waypoints.append(feature)
    return features, waypoints


def get_init_values(minute, related_req):
    h, m = divmod(minute, 60)
    parcels = []
    parcel_text = ""
    for p in related_req:
        parcels.append(p)
        parcel_text += str(p) + ", "
    parcel_str = parcel_text[:len(parcel_text) - 2]
    return h, m, parcels, parcel_str


def get_mode_change(action):
    """
    Creates a mode_change feature.
    :param action: All the information about the action object of the mode_change.
    :return: A mode_change feature object.
    """
    h, m = divmod(action.minute, 60)
    loc = get_location(action.nodes, get_nearest_node(action.vehicle, action.minute))
    feature = Feature(geometry=Point(loc),
                properties={
                    "type": "mode_change",
                    "name": "Mode change",
                    "title": "Change from " + action.vehicle["mode"][str(action.minute)] + " to " + get_next_mode(action.vehicle, action.minute),
                    "route_number": action.num,
                    "arrival_h": h,
                    "arrival_m": m,
                    "duration": action.action["duration"],
                    "distance": 0,
                    "vehicle": action.num,
                    "arrival_mode": get_prev_mode(action.vehicle, action.minute)
                })
    return feature


def get_delayed(action):
    """
    Creates a delay feature.
    :param action: All the information about the action object of the delay.
    :return: A delay feature object.
    """
    h, m = divmod(action.minute, 60)
    loc = get_location(action.nodes, get_nearest_node(action.vehicle, action.minute))
    feature = Feature(geometry=Point(loc),
                      properties={
                          "type": "delayed",
                          "name": "Delay",
                          "title": "Vehicle "+str(action.num)+" delayed",
                          "route_number": action.num,
                          "arrival_h": h,
                          "arrival_m": m,
                          "distance": 0,
                          "vehicle": action.num,
                          "duration": action.action["duration"],
                          "arrival_mode": get_prev_mode(action.vehicle, action.minute)
                      })
    return feature


def get_depot_index(depots, id):
    """
    Find the index of a depot by id.
    :param depots: A list of depots.
    :param id: The identifier of the depot to find.
    :return: The index of a depot.
    """
    for i in range(0, len(depots)):
        if depots[i].properties["number"] == id:
            return i
    return -1


def remove(parcels, load):
    """
    Remove parcels in the load from the parcel list.
    :param parcels: A list of parcels.
    :param load: The list of parcels to remove.
    :return: A list of parcels without those in load.
    """
    res = []
    for p in parcels:
        if p not in load:
            res.append(p)
    return res


def get_location(nodes, id):
    """
    Retrieve the coordinates of a node.
    :param nodes: The list of nodes.
    :param id: The id of the node for which to find the location.
    :return: The coordinate values of the given node.
    """
    for node in nodes:
        if node["id"] == id:
            return node["coordinates"]["longitude"], node["coordinates"]["latitude"]
    return -1


def get_prev_mode(vehicle, minute):
    """
    Retrieve the mode with which a vehicle arrives at a location.
    :param vehicle: The vehicle for which to find the mode.
    :param minute: The moment the mode change occurs.
    :return: The mode (Autonomous vs Manual) that the vehicle will take on.
    """
    for i in range(minute, 0, -1):
        for action in make_list(vehicle["actions"], i):
            if action["actionType"] == "TRAVELLING":
                return vehicle["mode"][str(i)]


def get_next_mode(vehicle, minute):
    """
    Retrieve the mode with which a vehicle departs from a mode change feature.
    :param vehicle: The vehicle for which to find the mode.
    :param minute: The moment the mode change occurs.
    :return: The mode (Autonomous vs Manual) that the vehicle will take on.
    """
    for i in range(minute, len(vehicle["actions"])):
        for action in make_list(vehicle["actions"], i):
            if action["actionType"] == "TRAVELLING":
                return vehicle["mode"][str(i)]


def get_last_node(vehicle, minute):
    for i in range(minute, 0, -1):
        for action in make_list(vehicle["actions"], i):
            if action["actionType"] == "TRAVELLING":
                return action["to"]


def get_nearest_node(vehicle, minute):
    """
    Retrieve the node at which a current event takes place.
    :param vehicle: The vehicle for which to find the mode.
    :param minute: The moment the mode change occurs.
    :return: The mode (Autonomous vs Manual) that the vehicle will take on.
    """
    for i in range(minute, len(vehicle["actions"])):
        for action in make_list(vehicle["actions"], i):
            if action["actionType"] == "TRAVELLING":
                return action["from"]
    for i in range(minute, 0, -1):
        for action in make_list(vehicle["actions"], i):
            if action["actionType"] == "TRAVELLING":
                return action["to"]


def get_req_dest(requests, nodes, dlv):
    """
    Retrieve the location of a delivery.
    :param requests: The list of all requests.
    :param nodes: The list of all nodes.
    :param dlv: identifier of the request.
    :return: The coordinates of the delivery.
    """
    for req in requests:
        if req["id"] == dlv:
            return get_location(nodes, req["destination"])


def get_origin_depot(requests, dlv):
    """
    Retrieve the depot node where a parcel is initially.
    :param requests: The list of all requests.
    :param dlv: identifier of the request.
    :return: The node id of the origin depot.
    """
    for req in requests:
        if req["id"] == dlv:
            return req["origin"]


def check_for_depot(nodes, loc):
    for node in nodes:
        if node["id"] == loc:
            return node["pickup"] == 1
