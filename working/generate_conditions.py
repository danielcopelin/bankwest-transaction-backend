import csv

def gen_conditionals_from_csv(src):
    categories = {}
    with open(src) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            categories[row[0]] = [c for c in row[1:] if c != '']

    category_column = 'Category'

    conditional_dict = {}
    conditional_dict['id'] = category_column
    conditional_dict['dropdowns'] = [
        {
            'condition': f'{{{category_column}}} eq "{category_item}"',
            'dropdown': [
                {'label': i, 'value': i} 
                for i in categories[category_item]
            ]
        } for category_item in categories.keys()
    ]

    return [conditional_dict]

src = 'working\\data\\categories.csv'
print(gen_conditionals_from_csv(src))