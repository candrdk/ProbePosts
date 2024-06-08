known_404 = [
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/8483F186-F115-413C-8753-3F018AC6EB2F-3991f21548560e00c72afff10f709f21.jpeg",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/65FFE8D0-63A1-496F-9273-18455CFB1237-76c3b44ec73fda54fee789240b7b62dd.png",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/IMG_20211225_162036705_HDR2-fe34231db26f67bf3c3dbd0265864c12.jpg",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/20211119_040144-539823a3a53b4495d744c75a0cb467ec.jpg",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/952FD36B-9FDA-4601-A4C8-838D856443BA-c2db6f4b19405f386f8446069b749dc3.jpeg",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/Screen-Shot-2021-12-28-at-11.51.18-AM-df6bd75a4307ff868eb37b585303ec68.png",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/20200811_231912-568f98f36cd058b4ef817aae093f6656.jpg"
]

raw_lines = []
img_lines = []

with open("dataset_raw.csv.old") as raw:
    raw_lines = [line.rstrip() for line in raw]
with open("image_urls.csv.old") as img:
    img_lines = [line.rstrip() for line in img]

assert len(raw_lines) == len(img_lines)

zipped = [*zip(raw_lines[1:],img_lines[1:])]
cleaned = [a for a in zipped if (a[1].split('.')[-1] in ['jpg','jpeg','png'] and a[1] not in known_404)]

with open("dataset_raw.csv", "w") as raw, open("image_urls.csv", "w") as img:

    raw.write(raw_lines[0] + '\n')
    img.write(img_lines[0] + '\n')

    raw.write('\n'.join(a[0] for a in cleaned))
    img.write('\n'.join(a[1] for a in cleaned))

