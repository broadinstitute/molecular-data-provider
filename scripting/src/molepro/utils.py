
def get_controls(**kwargs):
    controls = []
    for key, value in kwargs.items():
        name = key.replace('__',' ')
        if type(value) == list:
            for val in value:
                controls.append({
                    "name": name,
                    "value": val
                })
        else:
            controls.append({
                "name": name,
                "value": value
            })
    return controls
