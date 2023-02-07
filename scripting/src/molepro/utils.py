
def get_controls(**kwargs):
    controls = []
    for key, value in kwargs.items():
        name = key.replace('___','-')
        name = name.replace('__',' ')
        if type(value) == list:
            for val in value:
                controls.append({
                    "name": name,
                    "value": val
                })
        else:
            if value is not None:
                controls.append({
                    "name": name,
                    "value": value
                })
    return controls
