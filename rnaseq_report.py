#!/usr/bin/env python3

import os
from rnaseq_funcs import send_json_message

def make_json_report(make_json_report_params_d) -> None:
    analysis_path = make_json_report_params_d['analysis_path']
    send_message_script = make_json_report_params_d['send_message_script']
    task_id = make_json_report_params_d['task_id']
    analysis_record_id = make_json_report_params_d['analysis_record_id']
    trimmer = make_json_report_params_d['trimmer']
    aligner = make_json_report_params_d['aligner']
    sample_name_l = make_json_report_params_d['sample_name_l']
    sample_type_l = make_json_report_params_d['sample_type_l']
    report_dict = {
        'status': 'Pass', 
        'pipelineName': 'rmaseq', 
        'taskId': task_id, 
        'analysisRecordId': analysis_record_id,
        'error': 0, 
        'taskName': 'Report', 
        'data': []
    }
    if aligner == 'star_salmon':
        multiqc_path = '{}/results/multiqc/{}'.format(analysis_path, 'star_salmon')
    if aligner == 'star_rsem':
        multiqc_path = '{}/results/multiqc/{}'.format(analysis_path, 'star_rsem')
    report_seq_stat_dict = {
        'sort': 1, 
        'title': '测序数据信息', 
        'subtitle1': '测序数据质量评估', 
        'memo': '', 
        'table': {
            'data': [
                {
                    'content':'',
                    'path': '{}/multiqc_report_data/mqc_fastqc_sequence_counts_plot_1.txt'.format(multiqc_path), 
                    'memo': '', 
                    'preDes': '使用FastQC软件, 对测序数据进行统计', 
                    'title': '测序数据统计表', 
                    'postDes': ''
                }
            ]
        }, 
        'image': {
            'data': [
                {
                    'title': '样本的数据量统计图', 
                    'postDes': '其中Duplicate readsd的数量通过软件估计', 
                    'memo': '', 
                    'preDes': '', 
                    'path': '{}/multiqc_report_plots/png/mqc_fastqc_sequence_counts_plot_1.png'.format(multiqc_path)
                }
            ]
        },
        'subtitle2': ''
    }
    report_dict['data'].append(report_seq_stat_dict)

    report_seq_qc_dict = {
        'sort': 2, 
        'title': '数据质量', 
        'memo': '', 
        'preDes': '数据质控结果展示', 
        'image': {
            'data': [
                {
                    'sort': 1, 
                    'title': '', 
                    'postDes': 'reads中每个碱基的平均质量', 
                    'memo': '', 
                    'preDes': 'Reads的每个碱基平均质量图', 
                    'path': '{}/multiqc_report_plots/png/mqc_fastqc_per_base_sequence_quality_plot_1.png'.format(multiqc_path)
                }, 
                {
                    'sort': 2, 
                    'title': '', 
                    'postDes': '每个Reads的平均质量分布', 
                    'memo': '', 
                    'preDes': 'Reads的质量值', 
                    'path': '{}/multiqc_report_plots/png/mqc_fastqc_per_sequence_quality_scores_plot_1.png'.format(multiqc_path)
                }, 
                {
                    'sort': 3, 
                    'title': '', 
                    'postDes': '每个Reads的平均GC含量', 
                    'memo': '', 
                    'preDes': 'Reads的GC含量图', 
                    'path': '{}/multiqc_report_plots/png/mqc_fastqc_per_sequence_gc_content_plot_Counts.png'.format(multiqc_path)
                }, 
                {
                    'sort': 4, 
                    'title': '', 
                    'postDes': 'Reads长度分布统计', 
                    'memo': '', 
                    'preDes': 'Reads长度分布统计', 
                    'path': '{}/multiqc_report_plots/png/mqc_fastqc_sequence_length_distribution_plot_1.png'.format(multiqc_path)
                }, 
                {
                    'sort': 5, 
                    'title': '', 
                    'postDes': '使用GATK picards对duplicate reads进行统计', 
                    'memo': '', 
                    'preDes': 'Duplicate reads统计', 
                    'path': '{}/multiqc_report_plots/png/mqc_picard_deduplication_1.png'.format(multiqc_path)
                }
            ]
        }, 
        'subtitle2': ''
    }
    report_dict['data'].append(report_seq_qc_dict)

    report_align_dict = {
        'sort': 3, 
        'title': '比对基因组', 
        'subtitle1': '比对结果统计', 
        'memo': '', 
        'table': {
            'sort': 1, 
            'data': [
                {
                    'content':'',
                    'path': '{}/multiqc_report_data/mqc_star_alignment_plot_1.txt'.format(multiqc_path), 
                    'memo': '', 
                    'preDes': '使用STAR比对参考基因组', 
                    'title': '样本比对情况', 
                    'postDes': ''
                }
            ]
        }, 
        'image': {
            'data': [
                {
                    'sort': 1, 
                    'title': ' 样本比对统计图', 
                    'postDes': '', 
                    'memo': '', 
                    'preDes': '', 
                    'path': '{}/multiqc_report_plots/png/mqc_star_alignment_plot_1.png'.format(multiqc_path)
                },
                {
                    'sort': 2, 
                    'title': '使用samtools stats 统计样本比对结果', 
                    'postDes': '', 
                    'memo': 'Alignment metrics from samtools stats; mapped vs. unmapped reads vs. reads mapped with MQ0.', 
                    'preDes': '', 
                    'path': '{}/multiqc_report_plots/png/mqc_samtools_alignment_plot_1.png'.format(multiqc_path)
                },
                {
                    'sort': 3, 
                    'title': 'reads基因组位置统计', 
                    'postDes': '', 
                    'memo': 'Classification of mapped reads as originating in exonic, intronic or intergenic regions. These can be displayed as either the number or percentage of mapped reads.', 
                    'preDes': '', 
                    'path': '{}/multiqc_report_plots/png/mqc_qualimap_genomic_origin_1.png'.format(multiqc_path)
                },
                {
                    'sort': 4, 
                    'title': '基因覆盖深度统计图', 
                    'postDes': '', 
                    'memo': 'Mean distribution of coverage depth across the length of all mapped transcripts', 
                    'preDes': '', 
                    'path': '{}/multiqc_report_plots/png/mqc_qualimap_gene_coverage_profile_Counts.png'.format(multiqc_path)
                }
            ]
        },
        'subtitle2': ''
    }
    report_dict['data'].append(report_align_dict)

    if aligner == 'star_salmon':
        report_quant_dict = {
            'sort': 4, 
            'title': '基因表达定量', 
            'subtitle1': '', 
            'memo': 'Salmon 是一款专门用于估计RNA-seq数据中基因表达量的工具。它通过基于概率的方法模型化了RNA-seq数据生成的过程，以更准确地估计基因的表达水平', 
            'table': {
                'data': [
                    {
                        'content':'',
                        'path': '{}/results/star_salmon/salmon.merged.gene_counts.tsv'.format(analysis_path), 
                        'memo': '', 
                        'preDes': '', 
                        'title': '基因表达量统计表', 
                        'postDes': ''
                    }
                ]
            },
            'subtitle2': ''
        }
        report_dict['data'].append(report_quant_dict)
    if aligner == 'star_rsem':
        report_quant_dict = {
            'sort': 4, 
            'title': '基因表达定量', 
            'subtitle1': '', 
            'memo': 'RSEM（RNA-Seq by Expectation-Maximization）是一个用于估计RNA-seq数据中基因表达水平的工具。采用概率建模的方法，同时使用了更为复杂的期望最大化（Expectation-Maximization, EM）算法', 
            'table': {
                'data': [
                    {
                        'content':'',
                        'path': '{}/results/star_rsem/rsem.merged.gene_counts.tsv'.format(analysis_path), 
                        'memo': '', 
                        'preDes': '', 
                        'title': '基因表达量统计表', 
                        'postDes': ''
                    }
                ]
            },
            'subtitle2': ''
        }
        report_dict['data'].append(report_quant_dict)
    report_reference_dict = {
        'sort': 5,
        'title': '分析工具及参考文献',
        'text': [
            {
                "sort": 1,
                "content": "[1] Di Tommaso P, Chatzou M, Floden EW, Barja PP, Palumbo E, Notredame C. Nextflow enables reproducible computational workflows. Nat Biotechnol. 2017 Apr 11;35(4):316-319. doi: 10.1038/nbt.3820. PubMed PMID: 28398311.",
                "memo": ""
            },
            {
                "sort": 2,
                "content": "[2] Ewels PA, Peltzer A, Fillinger S, Patel H, Alneberg J, Wilm A, Garcia MU, Di Tommaso P, Nahnsen S. The nf-core framework for community-curated bioinformatics pipelines. Nat Biotechnol. 2020 Mar;38(3):276-278. doi: 10.1038/s41587-020-0439-x. PubMed PMID: 32055031.",
                "memo": ""
            },
            {
                "sort": 3,
                "content": "[3] Ewels P, Magnusson M, Lundin S, Käller M. MultiQC: summarize analysis results for multiple tools and samples in a single report. Bioinformatics. 2016 Oct 1;32(19):3047-8. doi: 10.1093/bioinformatics/btw354. Epub 2016 Jun 16. PubMed PMID: 27312411. PubMed Central PMCID: PMC5039924.",
                "memo": ""
            },
            {
                "sort": 4,
                "content": "[4] Li, B., Dewey, C. N. (2011). RSEM: accurate transcript quantification from RNA-Seq data with or without a reference genome. BMC Bioinformatics, 12:323. DOI: 10.1186/1471-2105-12-323",
                "memo": ""
            },
            {
                "sort": 5,
                "content": "[5] Dobin, A., Davis, C. A., Schlesinger, F., Drenkow, J., Zaleski, C., Jha, S., ... & Gingeras, T. R. (2013). STAR: ultrafast universal RNA-seq aligner. Bioinformatics, 29(1), 15-21. DOI: 10.1093/bioinformatics/bts635",
                "memo": ""
            },
            {
                "sort": 6,
                "content": "[6] Patro, R., Duggal, G., Love, M. I., Irizarry, R. A., & Kingsford, C. (2017). Salmon provides fast and bias-aware quantification of transcript expression. Nature Methods, 14(4), 417-419. DOI: 10.1038/nmeth.4197",
                "memo": ""
            },
            {
                "sort": 7,
                "content": "[7] Okonechnikov, K., Conesa, A., & García-Alcalde, F. (2016). Qualimap 2: advanced multi-sample quality control for high-throughput sequencing data. Bioinformatics, 32(2), 292-294. DOI: 10.1093/bioinformatics/btv566",
                "memo": ""
            },
            {
                "sort": 8,
                "content": "[8] Wang, L., Wang, S., & Li, W. (2012). RSeQC: quality control of RNA-seq experiments. Bioinformatics, 28(16), 2184-2185. DOI: 10.1093/bioinformatics/bts356",
                "memo": ""
            },
            {
                "sort": 9,
                "content": "[9] Martin, M. (2011). Cutadapt removes adapter sequences from high-throughput sequencing reads. EMBnet. journal, 17(1), 10-12. DOI: 10.14806/ej.17.1.200",
                "memo": ""
            }
        ]
    }
    report_dict['data'].append(report_reference_dict)

    for file in os.listdir('{}/results/pipeline_info'.format(analysis_path)):
        if file.startswith('execution_report'):
            execution_report_file_path = '{}/results/pipeline_info/{}'.format(analysis_path, file)
        if file.startswith('execution_timeline'):
            execution_timeline_file_path = '{}/results/pipeline_info/{}'.format(analysis_path, file)
        if file.startswith('pipeline_dag'):
            pipeline_dag_file_path = '{}/results/pipeline_info/{}'.format(analysis_path, file)
    report_download_dict = {
        'sort': 6, 
        'title': '可视化报告下载', 
        'text': [
            {
                'sort':1,
                'title': 'MultiQC报告',
                'content': 'MultiQC报告下载：#&{}/multiqc_report.html'.format(multiqc_path), 
                'postDes': '', 
                'memo': '', 
                'preDes': ''
            },
            {
                'sort':2,
                'title': '分析流程运行监控报告',
                'content': '分析流程运行监控报告下载：#&{}'.format(execution_report_file_path), 
                'postDes': '', 
                'memo': '', 
                'preDes': '详细展示了各分析模块的资源使用情况'
            },
            {
                'sort':3,
                'title': '分析流程运行时间报告',
                'content': '分析流程运行时间监控报告下载：#&{}'.format(execution_timeline_file_path), 
                'postDes': '', 
                'memo': '', 
                'preDes': '详细展示了各分析模块的运行时间情况'
            }
        ], 
        'memo': '', 
        'subtitle1': '', 
        'subtitle2': ''
    }
    report_dict['data'].append(report_download_dict)
    # {
    #     'sort':4,
    #     'title': '分析模块逻辑关系',
    #     'content': '分析流程中各模块的逻辑关系报告下载：#&{}'.format(pipeline_dag_file_path), 
    #     'postDes': '', 
    #     'memo': '', 
    #     'preDes': '详细展示了各分析模块间的逻辑关系'
    # }

    send_json_message(analysis_path, send_message_script, report_dict, 'Report.json')