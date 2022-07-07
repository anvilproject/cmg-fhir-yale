#!/usr/bin/env python

"""
 The convention for these datasets is to stash diseases into single corresponding field where multiples are separated by the pipe "|". We'll create a separate file with these expanded as well as create corresponding harmony entries suitable for Whistler harmonization

 In addition to potential codes, there is also a free text disease field which may be the only field with data. 

 a affected_status field relates to the status associated with the specified disease
"""

import sys
import csv 
from term_lookup import pull_details
import pdb
from argparse import ArgumentParser

motifs = {}

subject_filenames = {
    "ds-mc": "../data/ds-mc/Subject_CMG_Yale_phs000744_DS-MC_20201218_Y9Q1.csv",
    "ds-rare": "../data/ds-rare/Subject_CMG_Yale_phs000744_DS-RARED_20201202_Y9Q1.csv",
    "hmb": "../data/hmb/Subject_CMG_Yale_phs000744_HMB_20201218_Y9Q1.csv",
    "gru": "../data/gru/Subject_CMG_Yale_phs000744_GRU_20201218_Y9Q1.csv"
}

parser = ArgumentParser(description="Pull out HP Codes and pull the details from web")
parser.add_argument(
    "-c",
    "--consent-group",
    required=True,
    choices=list(subject_filenames.keys()) + ['ALL'],
    help="Which consent group(s) to pull"
)
args = parser.parse_args()
filenames = []
if args.consent_group == "ALL":
    for consent in subject_filenames:
        filenames.append(subject_filenames[consent])
else:
    filenames.append(subject_filenames[args.consent_group])

for filename in filenames:
    with open(f"../output/diseases-{args.consent_group}.csv", "wt") as outf:
        writer = csv.writer(outf)
        writer.writerow([
            "subject_id",
            "condition_code",
            "condition_name",
            "affected_status",
            "disease_description",
            "phenotype_description"
        ])

        with open(filename, 'rt') as f:
            reader = csv.DictReader(f)

            for line in reader:
                #pdb.set_trace()

                codes = []

                if line['disease_id'].strip() != "":
                    if "|" in line['disease_id']:
                        codes = line['disease_id'].strip().split("|")
                    else:
                        codes = line['disease_id'].strip().split(";")

                if len(codes) == 0:
                    writer.writerow([
                        line['subject_id'],
                        "",
                        "",
                        line['affected_status'],
                        line['disease_description'],
                        line['phenotype_description']
                    ])  
                else:              
                    for id in codes:
                        details = pull_details(id)

                        if details:
                            writer.writerow([
                                line['subject_id'],
                                id,
                                details.name,
                                line['affected_status'],
                                line['disease_description'],
                                line['phenotype_description']
                            ])

                            motifs[id] = [
                                id,
                                details.name,
                                "subject",
                                "disease_id",
                                "disease_id",
                                details.code,
                                details.name,
                                details.system,
                                ""
                            ]
                        else:
                            print(f"Unable to find, {id}. Skipping it.")

with open(f"../output/disease-codes-{args.consent_group}.csv", "wt") as f:
    writer = csv.writer(f)

    writer.writerow(["local code",
                    "text",
                    "table_name",
                    "parent_varname",
                    "local code system",
                    "code",
                    "display",
                    "code system",
                    "comment"])

    for id in sorted(motifs.keys()):
        writer.writerow(motifs[id])
