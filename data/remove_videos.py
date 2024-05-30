



raw_lines = []
img_lines = []

with open("dataset_raw.csv") as raw:
    raw_lines = [line.rstrip() for line in raw]
with open("image_urls.csv") as img:
    img_lines = [line.rstrip() for line in img]

assert len(raw_lines) == len(img_lines)

zipped = [*zip(raw_lines[1:],img_lines[1:])]



cleaned = [a for a in zipped if a[1].split('.')[-1] in ['jpg','jpeg','png']]

with open("dataset_raw_new.csv", "w") as raw, open("image_urls_new.csv", "w") as img:

    raw.write(raw_lines[0])
    img.write(img_lines[0])

    raw.write('\n'.join(a[0] for a in cleaned))
    img.write('\n'.join(a[1] for a in cleaned))

