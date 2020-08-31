#Formatting data

## Formatting the retrieved hits

```
usage : python retrieve_to_csv.py path_in path_out

positional arguments:
    path_in   path of the .pkl file containing the raw information from the hit
    path_out  path of the .csv file where to write

optional arguments:
    -a, --keep_attention   Whether to keep the attention checks in the output or in a seperate file (default: False, which means attention in a seperate file)
    -i, --hit_id           Whether to add hit_id to the csv (default : False)

```

## Transforming a 4pt scale to 3pt and 2pt
The script to_2point.py transforms to both 3points and 2points
```
usage : python to_2point.py path_in path_out

positional arguments:
    path_in    path of a .csv containing UID, ANSWER, ANNOTATOR columns
    path_out   path of a directory where to save the 2pt and 3pt, path of files will be path_out/2pt_{basename(path_in)}
```


## Format for web interface

format.py is used to transform the csv in a format usable by the web interface of AMT