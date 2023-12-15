#!/usr/bin/env python3

import os
import time
from rnaseq_funcs import send_json_message


def monitor_execution(monitor_execution_params_d) -> None:
    analysis_path = monitor_execution_params_d['analysis_path']
    send_message_script = monitor_execution_params_d['send_message_script']
    return_value = monitor_execution_params_d['return_value']
    start_time = monitor_execution_params_d['start_time']
    task_id = monitor_execution_params_d['task_id']
    analysis_record_id = monitor_execution_params_d['analysis_record_id']
    os.chdir(analysis_path)
    step_dict = {
        'tTaskId': task_id,
        'analysisRecordId': analysis_record_id,
        'pipelineName': 'rnaseq',
        'analysisStatus': '',
        'startDate': start_time,
        'endDate': '',
        'error': 0,
        'taskName': 'Step'
    }
# start        0  1  1  1  1  1  流程开始
# pre          0  0  1  1  1  1  数据预处理
# align        0  0  0  1  1  1  比对基因组及定量
# post         0  0  0  0  1  1  比对后处理
# multiqc      0  0  0  0  0  1  可视化报告
# step_flag    0  1  2  3  4  5
# step_flag    0  流程开始
# step_flag    1  数据预处理
# step_flag    2  比对基因组及定量
# step_flag    3  比对后处理
# step_flag    4  可视化报告

    step_flag = 0  # 流程开始
    # send the message of step_0
    time.sleep(60)
    step_dict['analysisStatus'] = '流程开始'
    step_file_name = 'step_start.json'
    if return_value == 0 and os.path.exists('{}/results'.format(analysis_path)):
        step_dict['endDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        step_dict['error'] = 0
        send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
        step_flag = 1
    else:
        step_dict['endDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        step_dict['error'] = 1
        send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
        exit('sarek startup failed')
    # send the message of step_x
    while True:
        if 'pipeline_info' in os.listdir(os.getcwd() + '/results'):
            execution_trace_file += '/pipeline_info'
            for file in os.listdir(execution_trace_file):
                if file.startswith('execution_trace'):
                    execution_trace_file += '/{}'.format(file)
                    break
            if 'execution_trace' in execution_trace_file:
                break
        time.sleep(60)
    while True:
        # if cancel.txt or Cancel.txt is found, kill the pipeline and exit
        if os.path.exists('{}/cancel.txt'.format(analysis_path)) or os.path.exists('{}/Cancel.txt'.format(analysis_path)):
            step_dict['error'] = 2
            step_dict['endDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            if os.path.exists('{}/.nextflow.pid'.format(analysis_path)):
                with open('{}/.nextflow.pid'.format(analysis_path)) as f:
                    os.system('kill {}'.format(f.read().strip('/n')))
            send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
            exit('The analysis was cancelled')
        with open(execution_trace_file, encoding = 'UTF-8') as trace_f:
            for line in trace_f:
                if step_flag == 1:  #  数据预处理
                    step_file_name = 'step_pre.json'
                    if ('FASTQ_FASTQC_UMITOOLS_TRIMGALORE:FASTQC' in line) or ('FASTQ_FASTQC_UMITOOLS_FASTP:FASTP' in line):
                        step_dict['startDate'] = line.split('\t')[6][:-4]
                        step_dict['analysisStatus'] = '数据预处理'
                        continue
                    if ('ALIGN_STAR:STAR_ALIGN' in line) or ('QUANTIFY_RSEM:RSEM_CALCULATEEXPRESSION' in line):
                        step_dict['endDate'] = line.split('\t')[6][:-4]
                        step_dict['error'] = 0
                        send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
                        step_flag = 2
                        continue
                    if ('FAILED' in line) or ('ABORTED' in line):
                        step_dict['endDate'] = line.split('\t')[6][:-4]
                        step_dict['error'] = 1
                        send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
                        exit('Failed or aborted in the step_pre')
                if step_flag == 2:  # 比对基因组
                    step_file_name = 'step_align.json'
                    if ('ALIGN_STAR:STAR_ALIGN' in line) or ('QUANTIFY_RSEM:RSEM_CALCULATEEXPRESSION' in line):
                        step_dict['startDate'] = line.split('\t')[6][:-4]
                        step_dict['analysisStatus'] = '比对基因组及定量'
                        continue
                    if ('ALIGN_STAR:BAM_SORT_STATS_SAMTOOLS:BAM_STATS_SAMTOOLS:SAMTOOLS_IDXSTATS' in line ) or ('QUANTIFY_RSEM:BAM_SORT_STATS_SAMTOOLS:BAM_STATS_SAMTOOLS:SAMTOOLS_IDXSTATS' in line):
                        step_dict['endDate'] = line.split('\t')[6][:-4]
                        step_dict['error'] = 0
                        send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
                        step_flag = 3
                        continue
                    if ('FAILED' in line) or ('ABORTED' in line):
                        step_dict['endDate'] = line.split('\t')[6][:-4]
                        step_dict['error'] = 1
                        send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
                        exit('Failed or aborted in the step_align')
                if step_flag == 3:  # 比对后处理
                    step_file_name = 'step_post.json'
                    if ('ALIGN_STAR:BAM_SORT_STATS_SAMTOOLS:BAM_STATS_SAMTOOLS:SAMTOOLS_IDXSTATS' in line ) or ('QUANTIFY_RSEM:BAM_SORT_STATS_SAMTOOLS:BAM_STATS_SAMTOOLS:SAMTOOLS_IDXSTATS' in line):
                        step_dict['startDate'] = line.split('\t')[6][:-4]
                        step_dict['analysisStatus'] = '比对后处理'
                        continue
                    if 'BAM_RSEQC:RSEQC_READDUPLICATION' in line:
                        step_dict['endDate'] = line.split('\t')[6][:-4]
                        step_dict['error'] = 0
                        send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
                        step_flag = 4
                        continue
                    if ('FAILED' in line) or ('ABORTED' in line):
                        step_dict['endDate'] = line.split('\t')[6][:-4]
                        step_dict['error'] = 1
                        send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
                        exit('Failed or aborted in the step_post_process')
                if step_flag == 4:  # 可视化报告
                    step_file_name= 'step_multiqc.json'
                    if 'BAM_RSEQC:RSEQC_READDUPLICATION' in line:
                        step_dict['startDate'] = line.split('\t')[6][:-4]
                        step_dict['analysisStatus'] = '可视化报告'
                        continue
                    if 'MULTIQC' in line:
                        step_dict['endDate'] = line.split('\t')[6][:-4]
                        step_dict['error'] = 0
                        send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
                        break
                    if ('FAILED' in line) or ('ABORTED' in line):
                        step_dict['endDate'] = line.split('\t')[6][:-4]
                        step_dict['error'] = 1
                        send_json_message(analysis_path, send_message_script, step_dict, step_file_name)
                        exit('Failed or aborted in the step_multiqc')

