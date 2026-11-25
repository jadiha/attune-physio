# data/

Everything in here except this file is git-ignored. Nothing in this folder is ever committed.

```
data/raw/apple_health_export/   Apple Health export (iPhone: Health > profile > Export All Health Data), unzipped
data/raw/mcphases/              mcPHASES v1.0.0 from PhysioNet (credentialed access, restricted license)
data/raw/flo/                   Flo export, when it arrives
data/processed/                 Tables the scripts write
```

On this machine `raw/apple_health_export` and `raw/mcphases` are symlinks to the folders on the Desktop,
so the data is never copied around.

## Getting mcPHASES

Request access at https://physionet.org/content/mcphases/ (needs a PhysioNet account and the
data use agreement). The PhysioNet Restricted Health Data License does not allow redistributing the data,
so anyone running this repo has to download it themselves.
