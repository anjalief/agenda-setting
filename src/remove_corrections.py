# import csv

# fp1 = open("./nyt_monthly.csv")
# fp2 = open("./nyt_monthly_clean.csv", "w")
# reader1 = csv.reader(fp1, delimiter=',')
# writer2 = csv.writer(fp2, delimiter=',')

# for row in reader1:
#     if "Correction" in row[2]:
#         continue
#     writer2.writerow(row)

lines = open("./nyt_monthly.csv").readlines()
fp2 = open("/projects/tir1/users/anjalief//nyt_monthly_clean2.csv", "w")
for line in lines:
    if not "Correction" in line:
        fp2.write(line)
fp2.close()
