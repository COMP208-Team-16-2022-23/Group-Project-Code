

def analysis(df, para_received):
    analytical_method = para_received["analytical_method"]
    return {
        "mean": k_nearest_neighbor(df, para_received),
    }.get(analytical_method, None)

def k_nearest_neighbor(df, para_received):
    y = para_received["dependent_variable_y"]
    x = para_received["independent_variable_x"]
    data_shuffling = para_received["data_shuffling"]
    training_set_ratio = para_received["training_set_ratio"]
    cross_validation = para_received["cross_validation"]
    number_of_neighbors = para_received["number_of_neighbors"]
    vector_distance_algorithm = para_received["vector_distance_algorithm"]
    search_algorithm = para_received["search_algorithm"]
    weighting_function_of_nearest_neighbors = para_received["weighting_function_of_nearest_neighbors"]

