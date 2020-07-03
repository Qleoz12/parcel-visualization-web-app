import pyrosm


# Warning, running this for big area's (such as the netherlands) will take 15+ minutes
if __name__ == "__main__":
  fp = pyrosm.get_data("netherlands")

  print(fp);

  # osm = pyrosm.OSM(fp)

  # street_network = osm.get_data_by_custom_criteria(
  #   custom_filter={'maxspeed': ['80', '100', '130']},
  #   filter_type="keep",
  #   # Do not keep nodes (point data)
  #   keep_nodes=False,
  #   keep_ways=True,
  #   keep_relations=True
  # )

  # # Overrides file if already present
  # street_network.to_file("./80100130.geojson", driver='GeoJSON')
