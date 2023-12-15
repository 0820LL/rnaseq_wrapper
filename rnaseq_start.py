#!/usr/bin/env python3

import argparse
import time
import os
import json
from rnaseq_step import monitor_execution
from rnaseq_report import make_json_report

def make_csv_file(analysis_path, patient_name, sample_type_l, sample_name_l, sample_file_l) -> str:
    csv_file = '{}/samples_sheet.csv'.format(analysis_path)
    csv_header = 'sample,fastq_1,fastq_2,strandedness'
    csv_content = ''
    for index in range(0, len(sample_file_l)):
        csv_content += '{},{},auto\n'.format(sample_name_l[index], sample_file_l[index]) 
    with open(csv_file, 'w') as csv_f:
        csv_f.write(csv_header + '\n')
        csv_f.write(csv_content[:-1])
    return csv_file

def make_params_file() -> str:
    pass

def steward(config_file_path, rnaseq_path, fasta_path, gtf_path, send_message_script) -> None:
    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    analysis_path = os.path.dirname(config_file_path)
    os.chdir(analysis_path)
    # get the parameters from the config.json file
    with open(config_file_path, 'r') as config_f:
        config_file_d = json.load(config_f)
    task_id = config_file_d['taskId']
    analysis_record_id = config_file_d['analysisRecordId']
    task_name = config_file_d['taskName']
    pipeline_name = config_file_d['pipeline']
    if 'patientId2' in config_file_d:
        patient_name = config_file_d['patientId2']
    else:
        patient_name = '--'
    trimmer = config_file_d['parameterList']['trimmer']
    aligner = config_file_d['parameterList']['aligner']
    min_mapped_reads = config_file_d['parameterList']['min_mapped_reads']
    if config_file_d['parameterList']['skip_trimming'] == 'trim':
        skip_trimming = False
    else:
        skip_trimming = True
    if config_file_d['parameterList']['skip_markduplicates'] == 'mark_duplicate':
        skip_markduplicates = False
    else:
        skip_markduplicates = True
    if not patient_name:
        patient_name = '--'
    sample_name_l = []
    sample_type_l = []
    sample_file_l = []
    sample_id_l = []
    for sample in config_file_d['taskSampleList']:
        sample_name_l.append(sample['sampleName'])  # the sample name
        sample_type_l.append(sample['sampleType'].lower())  # the sample type, [ tumor | normal ]
        sample_file_l.append('{},{}'.format(sample['read1'], sample['read2']))  # the fastq file including R1 and R2
        sample_id_l.append(sample['sampleId'])
    os.chdir(analysis_path)
    csv_file = make_csv_file(analysis_path, patient_name, sample_type_l, sample_name_l, sample_file_l)
    params_d = {
        'input':csv_file,
        'timmer':trimmer,
        'aligner':aligner,
        'min_mapped_reads':int(min_mapped_reads),
        'skip_trimming':skip_trimming,
        'skip_markduplicats':skip_markduplicates,
        'fasta':fasta_path,
        'gtf':gtf_path,
        'outdir':'results'
    }
    params_file_path = '{}/params.json'.format(analysis_path)
    with open(params_file_path, 'w') as params_f:
        json.dumps(params_d, ensure_ascii=False, fp=params_f, indent=4)
    rnaseq_command = 'nextflow run -offline -profile singularity -bg -params-file {} {} >> run_rnaseq.log'.format(params_file_path, rnaseq_path)
    return_value = os.system(rnaseq_command)
    with open('rnaseq_command.txt', 'w') as rnaseq_command_f:
        rnaseq_command_f.write(rnaseq_command + '\n')
        rnaseq_command_f.write('return value:{}\n'.format(str(return_value)))
    # to monitor the pipeline execution status and send messages
    monitor_execution_params_d = {
        'analysis_path':analysis_path,
        'send_message_script':send_message_script,
        'return_value':return_value,
        'start_time':start_time,
        'task_id':task_id,
        'analysis_record_id':analysis_record_id,
    }
    monitor_execution(monitor_execution_params_d)
    # to generate the report json file
    make_json_report_params_d = {
        'analysis_path': analysis_path,
        'send_message_script': send_message_script,
        'task_id': task_id,
        'analysis_record_id': analysis_record_id,
        'trimmer': trimmer,
        'aligner': aligner,
        'sample_name_l': sample_name_l,
        'sample_type_l': sample_type_l
    }
    make_json_report(make_json_report_params_d)


def main() -> None:
    parser = argparse.ArgumentParser(description='transfer the config.json to csv file; invoke the rnaseq pipeline; feedback the information to front end')
    parser.add_argument('--cfp',required=True, help='the full path for the config.json file')
    parser.add_argument('--rnaseq_path', required=True, help='the full path for rnaseq')
    parser.add_argument('--fasta', required=True, help='the full path for genome fasta file')
    parser.add_argument('--gtf', required=True, help='the full path for the genome gtf file')
    parser.add_argument('--send_message_script', required=True, help='the full path for the shell script: sendMessage.sh')
    args = parser.parse_args()
    config_file_path = args.cfp
    rnaseq_path = args.rnaseq_path
    fasta_path = args.fasta
    gtf_path = args.gtf
    send_message_script = send_message_script
    steward(config_file_path, rnaseq_path, fasta_path, gtf_path, send_message_script)


if __name__ == '__main__':
    main()
