<p align="center">
  <img src="docs/assets/logo-area.png" alt="Area logo" width="200"/>
</p>

# Nastro (NAnopore STream Optimized) 🧬

Nastro is an ultra-rapid, open-source computing pipeline specifically developed to handle the demanding computational workload of Oxford Nanopore Technologies' (ONT) PromethION sequencing device. It is designed to deliver exceptional speed for both basecalling and alignment, enabling near real-time data processing and analysis, thus reducing the time between sequencing and downstream results to near zero. 

## Key Features
- **Ultra-Fast Processing**: Nastro achieves significant reductions in processing time, ensuring quick transitions from raw sequencing data to actionable results.
- **Open-Source and Customizable**: Built using open-source technologies, Nastro is highly adaptable, allowing customization to meet project-specific requirements.
- **Parallel Processing with HPC**: At the heart of Nastro lies **ParallelCall**, an in-house developed tool that wraps around ONT's standard basecaller, Dorado. This software parallelizes the basecalling process across multiple computational nodes using a High Performance Computing (HPC) approach, scaling linearly with allocated resources.
- **Comprehensive Reporting**: The pipeline generates two detailed reports for each batch of data—one for basecalling and another for alignment—providing real-time feedback on experimental progress.
- **Asynchronous Data Flow**: Each step of the pipeline operates independently, allowing for simultaneous data processing streams, ensuring immediate batch results.
- **FAIR Data Management**: The design supports a customized samplesheet and metadata collection process, aligning with a Data Management Plan and implementing a fair-by-design approach for data handling.

## Why Nastro?
While ONT's MinKnow software provides a comprehensive solution for sequencing, basecalling, and alignment, it is limited by its design for single-unit computational setups. In contrast, Nastro, built on Jenkins—a powerful open-source automation server—enables flexible workflow customization and control. This adaptability translates into advanced data handling capabilities and optimized performance for diverse computational environments.

### Performance Benchmarks
Nastro’s efficiency was demonstrated using **2 Nvidia DGX nodes** from [**Area Science Park's Orfeo cluster**](https://orfeo-doc.areasciencepark.it/), where a 16x reduction in basecalling time was achieved compared to the standard ONT computational unit equipped with 4 Nvidia V100 GPUs.

## Pipeline Workflow
1. **Data Acquisition**: Automatically detects and integrates new data from the sequencing process.
2. **Parallel Basecalling**: Using **ParallelCall**, the pipeline distributes the basecalling workload across multiple computational nodes.
3. **Alignment**: Completed batches are aligned promptly using **MiniMap2**.
4. **Initial Analysis and Reporting**: Generates user-friendly reports for both basecalling and alignment, ensuring continuous feedback.

## Asynchronous Operation
Nastro supports an asynchronous flow, where each processing step runs independently, enabling parallel data streams. This results in minimal wait times between the availability of new data and the output of results.

## Open and Customizable Design
The pipeline was developed with flexibility and customization at its core. The personalized samplesheet and metadata collection process simplify integration into data management systems, promoting FAIR data handling principles by design.

## Get Started
Visit our [GitHub repository](#) to access the source code, installation instructions, and comprehensive documentation to deploy Nastro in your computational environment.

## Acknowledgments
Nastro was developed in collaboration with **Area Science Park's Orfeo cluster** to support advanced genomics and epigenomics research. Special thanks to our team for creating **ParallelCall** and ensuring its seamless integration into the pipeline.

---

Nastro aims to transform how sequencing data is processed, making ultra-rapid, real-time genomics analysis accessible and customizable for research projects worldwide.
