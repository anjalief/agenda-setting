# Result of k-fold tuning
DEFAULT_PARAMS = [
   50000,
   500,
   20,
   250,
   250,
   0.5,
   4
]

# Results of tobacco no-seed tuning
NOSEED_PARAMS = [
50000, 200, 25, 100, 500, 0.3, 1
]

# Results of tobacco tuning
# PRIMARY 0.6055214723926381; Economic; 0.823359534664459
TOBACCO_PARAMS = [
50000, 200, 50, 100, 250, 0.5, 2
]

# Testing clustering
CLUSTER_PARAMS = [
50000, 200, 25, 100, 250, 0.5, 4
]

# PRIMARY 0.5923312883435583
# Economic; 0.8415803782902861
FINAL_PARAMS = [
50000, 500, 50, 250, 500, 0.4, 3
]

RUSSIAN_PARAMS = [
50000, 500, 50, 250, 1000, 0.3, 3
]

# PRIMARY 0.5923312883435583
# Economic; 0.8415803782902861
PRIMARY1 = [
50000, 500, 75, 250, 500, 0.4, 3
]


# REALLY BAD
PRIMARY2 = [
50000, 1000, 25, 500, 500, 0.4, 3
]

class Params:
   def  __init__(self, p = FINAL_PARAMS):
       self.VOCAB_SIZE = p[0]
       self.MIN_CUT = p[1]
       self.MAX_CUT = p[2]
       self.TO_RETURN_COUNT = p[3]
       self.VEC_SEARCH = p[4]
       self.SIM_THRESH = p[5]
       self.LEX_COUNT = p[6]



# TOBACCO params seems to be better for main task
# DEAFULT params seem better for primary frame task
