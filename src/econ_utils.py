from datetime import date

# if you've provided a date_to_idx mapping, return
# idx_to_val, where idx corresponts to date_to_idx map
def load_monthly_gdp(filename, date_to_idx = None):
    idx_to_val = {}
    for line in open(filename).readlines():
        splits = line.split(",")
        if not splits[0]: # we have some blank lines
            continue
        val = float(splits[1].strip())
        date_split = splits[0].split("-")
        # assumes 1st of the month
        d = date(int(date_split[0]), int(date_split[1]), 1)

        if date_to_idx:
            # don't need econ data for dates we don't have articles for
            if d in date_to_idx:
                idx = date_to_idx[d]
                idx_to_val[idx] = val
        else:
            idx_to_val[d] = val



    return idx_to_val

def load_rtsi(filename, date_to_idx = None):
    idx_to_val = {}
    for line in open(filename).readlines():
        splits = line.split(",")
        if not splits[0]:
            continue
        vals = [float(x) for x in splits[1:]]

        # order in file is day.month.year
        date_split = splits[0].split(".")
        d = date(int(date_split[2]), int(date_split[1]), int(date_split[0]))

        if date_to_idx:
            if d in date_to_idx:
                idx = date_to_idx[d]
                idx_to_val[idx] = vals
        else:
            idx_to_val[d] = vals



    return idx_to_val
