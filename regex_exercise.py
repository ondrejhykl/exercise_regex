import re
import csv
import gzip
import os
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

# Task 1
log_lines = [
    "2024-01-15 10:02:11 INFO Server started on port 8080",
    "2024-01-15 10:03:47 ERROR Failed to connect to database",
    "2024-01-16 08:15:00 WARNING Disk usage at 85%",
    "2024-01-16 14:22:39 ERROR Timeout while fetching https://example.com/api",
    "2024-01-17 09:00:05 INFO User admin logged in from 192.168.1.10",
    "2024-01-17 11:41:18 DEBUG Cache cleared successfully",
    "2024-01-18 03:12:56 ERROR Connection refused from 192.168.1.55",
    "2024-01-18 23:59:02 INFO Backup completed in 42s",
]

a = [line for line in log_lines if re.match(r"2024-01-16", line)]
print(a)

b = [line for line in log_lines if re.search(r"ERROR|WARNING", line)]
print(b)

c = re.findall(r"\d{1,3}(?:\.\d{1,3}){3}", "\n".join(log_lines))
print(c)

d = [line for line in log_lines if re.search(r"in \d+s$", line)]
print(d)

e = [line for line in log_lines if re.search(r"https?://", line)]
print(e)

f = re.fullmatch(
    r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \w+ .+",
    log_lines[0]
)

print(f is not None)


# Task 2
def reverse_complement(sequence):
    complement = {
        "A": "T",
        "T": "A",
        "C": "G",
        "G": "C"
    }

    return "".join(complement[base] for base in sequence)[::-1]


class SequencingRead:
    def __init__(self, read_id, sequence):
        self.read_id = read_id
        self.sequence = sequence

    def matches_mid_pair(self, forward_mid, reverse_mid):
        comp_reverse = reverse_complement(reverse_mid)
        return re.match(rf"^{forward_mid}.+{comp_reverse}$", self.sequence) is not None

    def trim_mid_pair(self, forward_mid, reverse_mid):
        if self.matches_mid_pair(forward_mid, reverse_mid):
            return self.sequence[len(forward_mid):-len(reverse_mid)]
        else:
            return None

    def describe(self):
        return f"{type(self).__name__} {self.read_id} ({len(self.sequence)} bp)"


# Task 3
class Demultiplexer:
    def __init__(self, fasta_path, mid_table_path):
        self.reads = []

        with gzip.open(fasta_path, "rt") as handle:
            for record in SeqIO.parse(handle, "fasta"):
                read = SequencingRead(record.id, str(record.seq))
                self.reads.append(read)

        self.samples = []

        with open(mid_table_path, newline="") as handle:
            reader = csv.DictReader(handle, delimiter=";")

            for row in reader:
                label = f"{row['SampleID']}_{row['Description']}"
                forward_mid = row["FBarcodeSequence"]
                reverse_mid = row["RBarcodeSequence"]

                self.samples.append((label, forward_mid, reverse_mid))

        self.assigned = {
            label: []
            for label, forward_mid, reverse_mid in self.samples
        }

        self.unassigned = []

    def assign_reads(self):
        for read in self.reads:
            assigned = False

            for label, forward_mid, reverse_mid in self.samples:

                if read.matches_mid_pair(forward_mid, reverse_mid):
                    trimmed = read.trim_mid_pair(
                        forward_mid,
                        reverse_mid
                    )

                    self.assigned[label].append(
                        SequencingRead(read.read_id, trimmed)
                    )

                    assigned = True
                    break

                if read.matches_mid_pair(reverse_mid, forward_mid):
                    trimmed = read.trim_mid_pair(
                        reverse_mid,
                        forward_mid
                    )

                    self.assigned[label].append(
                        SequencingRead(read.read_id, trimmed)
                    )

                    assigned = True
                    break

            if not assigned:
                self.unassigned.append(read)

    def report(self):
        lines = []

        for label, reads in self.assigned.items():
            lines.append(f"{label}\t{len(reads)}")

        lines.append(f"unassigned\t{len(self.unassigned)}")

        return "\n".join(lines)

    def write_fasta(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        for label, reads in self.assigned.items():
            if not reads:
                continue

            output_path = os.path.join(
                output_dir,
                f"{label}.fasta"
            )

            records = [
                SeqRecord(
                    Seq(read.sequence),
                    id=read.read_id,
                    description=""
                )
                for read in reads
            ]

            SeqIO.write(records, output_path, "fasta")


if __name__ == "__main__":
    # Task 2
    r1 = SequencingRead("demo_1", "AGCTTCGA" + "N" * 20 + reverse_complement("TGCAGGTC"))
    print(r1.describe())
    print(r1.matches_mid_pair("AGCTTCGA", "TGCAGGTC"))  # True
    print(r1.matches_mid_pair("CGATCGAT", "GCTAGCTA"))  # False
    print(r1.trim_mid_pair("AGCTTCGA", "TGCAGGTC"))  # 20 x "N"

    # Task 3
    demux = Demultiplexer("fishes.fna.gz", "fishes_MIDs.csv")
    demux.assign_reads()
    print(demux.report())
    demux.write_fasta("demux_output")
