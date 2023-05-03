#!/usr/bin/python3
#
# data from https://wisevoter.com/state-rankings/states-by-population/

state_to_pop = {
    'CA': 40223504,
    'TX': 30345487,
    'FL': 22359251,
    'NY': 20448194,
    'PA': 13092796,
    'IL': 12807072,
    'OH': 11878330,
    'GA': 11019186,
    'NC': 10710558,
    'MI': 10135438,
    'NJ': 9438124,
    'VA': 8820504,
    'WA': 7999503,
    'AZ': 7379346,
    'MA': 7174604,
    'TN': 7080262,
    'IN': 6876047,
    'MD': 6298325,
    'MO': 6204710,
    'CO': 5997070,
    'WI': 5955737,
    'MN': 5827265,
    'SC': 5266343,
    'AL': 5097641,
    'LA': 4695071,
    'KY': 4555777,
    'OR': 4359110,
    'OK': 4021753,
    'CT': 3615499,
    'UT': 3423935,
    'IA': 3233572,
    'NV': 3225832,
    'AR': 3040207,
    'KS': 2963308,
    'MS': 2959473,
    'NM': 2135024,
    'NE': 2002052,
    'ID': 1920562,
    'WV': 1775932,
    'HI': 1483762,
    'NH': 1395847,
    'ME': 1372559,
    'MT': 1112668,
    'RI': 1110822,
    'DE': 1017551,
    'SD': 908414,
    'ND': 811044,
    'AK': 740339,
    'VT': 648279,
    'WY': 580817,
    'DC': 712816,  # 2020
    'AP': 1000000,  # random. armed forces, pacific
    'AA': 1000000,  # random. armed forces, americas
}

def count_accelerators(fh):
    state_count = {}
    for line in fh:
        fields = [f.strip() for f in line.split(',')]
        if fields[3] != 'US':
            continue
        state = fields[2]
        state_count[state] = state_count.get(state, 0) + 1
    return state_count

def main():
    with open('data.csv') as f:
        counts = count_accelerators(f)
    pop = [(k, n/state_to_pop[k]) for k,n in counts.items()]
    pop.sort(key=lambda a: a[1], reverse=True)
    for i in range(10):
        print(f'{pop[i][0]} {pop[i][1]}')
        

if __name__ == '__main__':
    main()
