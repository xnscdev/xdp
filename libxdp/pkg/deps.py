def check_option(result, options, dep_map, option, dep):
    if option in options:
        dep_map[dep] = option
        result.append(dep)
