# AMT Hit generation

## Support for new tasks

To add support to new tasks fill the task_dictionaries.py dictionaries with the appropriate task infos (look a the validity_4pt entries of the dictionaries).

You will need to add an instruction file which contains the instructions of the tasks formatted as html (look at ./instructions/validity_4pt.html for an example).


## Launching a HIT
### Prerequisite

```
pip install boto3
```

### Launching a Hit

```
usage: python launch_hit.py [-h] [--name NAME] [-b] [-n N] [--window WINDOW]
                     [--wage_per_judgement WAGE_PER_JUDGEMENT] [--duration DURATION]
                     [--lifetime LIFETIME] [--keywords KEYWORDS] [--description DESCRIPTION]
                     [--max_assignments MAX_ASSIGNMENTS] [--title TITLE] [--qualification]
                     [--hit_file HIT_FILE]
                     task path_csv

Launches AMT HITs for ranking task.

positional arguments:
  task                  task name
  path_csv              path towards the csv containing data

optional arguments:
  -h, --help            show this help message and exit
  --name NAME           hit name
  -b, --sandbox         Set to true to run in the sandbox.
  -n N                  Number of judgments (default 10)
  --window WINDOW       dialog window size (default 4)
  --wage_per_judgement WAGE_PER_JUDGEMENT
                        Wage per judgement (default 0.01)
  --duration DURATION   Assignment Duration in seconds
  --lifetime LIFETIME   Lifetime of the Hits
  --keywords KEYWORDS   Keywords of the HIT
  --description DESCRIPTION
  --max_assignments MAX_ASSIGNMENTS
  --title TITLE
  --qualification
  --hit_file HIT_FILE

```

### Retrieving hits
```
usage: python retrieve_responses.py [-d HIT_FILE] [-b] [-p] [-o] [--delete]

optional arguments:
    -d, --hit_list_path   Path to a .txt file with one HIT ID per line.
    -b, --sandbox         Set to true to run in the sandbox.
    -p, --pay             Set to true to pay the workers.
    -o, --out             amt_hit_responses.pkl
    --delete              supposed to take the hits off of AMT (not sure if it works)
```
Scripts to extract the useful informations off of the .pkl file can be found ~/python/format/retrieve_to_csv.py


## Generating html for web interface
### Prerequisite

Nothing

### Generating html

`python html_gen {path_to_instruction} {task}`

path_to_instruction is the path to a file containing html format instructions.

task is the name of the task (now only breakdown is supported, to add support, add entries to the dictionaries in html_gen.py)

```
optional arguments:
    -n              number of questions (default 5)
    --out_dir       path to the directory where to write output (default './hits')
```