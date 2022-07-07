#!/usr/bin/env python

"""
 The convention for these datasets is to stash all disease and phenotypes into a single corresponding field where multiples are separated by the pipe "|". We'll create a separate file with these expanded as well as create corresponding harmony entries suitable for Whistler harmonization
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
    with open(f"../output/conditions-{args.consent_group}.csv", "wt") as outf:
        writer = csv.writer(outf)
        writer.writerow([
            "subject_id",
            "condition_code",
            "condition_name",
            "present_absent"
        ])

        with open(filename, 'rt') as f:
            reader = csv.DictReader(f)

            for line in reader:
                #pdb.set_trace()
                is_present = True
                for hp_content in ["hpo_present", "hpo_absent"]:
                    # A few were erroneously separated by semicolons
                    if ";" in line[hp_content]:
                        codes = line[hp_content].split(";")
                    else:
                        codes = line[hp_content].split("|")
                    
                    for id in codes:
                        details = pull_details(id)

                        if details:
                            writer.writerow([
                                line['subject_id'],
                                id,
                                details.name,
                                is_present
                            ])

                            motifs[id] = [
                                id,
                                details.name,
                                "subject",
                                hp_content,
                                "subject",
                                details.code,
                                details.name,
                                details.system,
                                ""
                            ]
                        else:
                            print(f"Unable to find, {id}. Skipping it.")
                    is_present = False

with open(f"../output/hp-codes-{args.consent_group}.csv", "wt") as f:
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
