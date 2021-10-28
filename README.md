# VEP4Hail

The code in this reposetory helps to transform VEP JSON output (see [JSON lines](https://jsonlines.org/)) in a schema friendly JSON and also find the schem that matches VEP annotation of all your variants.

Hail internally implements [hail.vep function](https://hail.is/docs/0.2/methods/genetics.html#hail.methods.vep). This function executes VEP to get annotations in JSON format and then parse JSON annotations and put them in the dataset (MatrixTable rows).

To parse JSON annotations you need to provide the schema that matches annotation for all of your variants.
These schema are provided for VEP v85 (GRCh37) and VEP v95 (GRCh38) (see [here](https://hail.is/docs/0.2/methods/genetics.html#hail.methods.vep)).
However, VEP schema is subject to changes from version to version. It also depends on which options and pluggins you are using while running VEP. 

The major issue with the newer version of the VEP is that their JSON outputs are NOT schema friendly, mainly beacuase of an issue in the colocated variants' frequencies. This is a dictionay with allele in the `key` field and frequencies in `value` field (as a nested dictionary). See the exampel below. Note that the in a large dataset with many indels, there could be many different alleles. This is not schema friendly.

```json
"frequencies":
{
    "AT":
    {
        "amr":0,
        "afr":0,
        "eur":0.001,
        "eas":0.001,
        "sas":0
    },
    "ATT":
    {
        "amr":0,
        "afr":0,
        "eur":0.001,
        "eas":0.001,
        "sas":0
    }
}
```

The following fix could make it schema friendly. We simply transform the dict into a list and push the allele string inside the value field.

```json
"frequencies":
[
    {
        "allele": "AT",
        "amr":0,
        "afr":0,
        "eur":0.001,
        "eas":0.001,
        "sas":0
    },
    {
        "allele": "ATT",
        "amr":0,
        "afr":0,
        "eur":0.001,
        "eas":0.002,
        "sas":0
    }
]
```

## Using the program

The [process.py](src/process.py) read the VEP JSON output (uncompressed or bgzip compressed) and produce two output files: the schema-friendly JSON (bgzip compressed) and the schema that matches all the JSON records in the input file. Note that bgzip compressed corrected JSONs are loaded by Hail in parallel. 
By default the schema is produced in binary format (python `pickle`) but you can change this behaviour to write it into a text format using `--xx`

```bash
python process.py vep_output.json.bgz corrected.json.bgz schema.txt --as-string
```

## Multiple JSONs
In case the annotation results are stored in multiple JSON files, you may process them with `process.py` individually (let the schema to be stored in binary format). Then you can use [combine.py](src/combine.py) to merge all schema into one that matches all JSON records form all files. The output schema is written in text format

```bash
for p in 1..10
do
    python process.py vep-part${p}.json.bgz corrected-part${p}.json.bgz schema-part${p}.pickle
    python combine.py "schema-part*.pickle" schema-all.txt
done 
```

## Example
We have provided an example notebook that perform the following step
1. Use Hail to
    1. Load VCF file
    2. Drop samples (not needed for VEP)
    3. Export VCF in parallel (split into equally sized set of variants) so that we could process parts of date in parallel (the following two steps)
2. Run VEP for each VCF part
3. Run `process.py` for each VEP output
4. Combine the schema
5. Load corrected JSON files into Hail
6. Parse VEP annotaint in hail structure format.
7. A simple usecase for VEP annotations
