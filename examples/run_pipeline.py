from polymer_mineru_pipeline.config import PipelineConfig
from polymer_mineru_pipeline.pipeline_runner import PolymerPipeline


if __name__ == "__main__":
    config = PipelineConfig()
    pipeline = PolymerPipeline(config=config, out_dir="output_dataset")

    pdf_files = [
        "data/paper1_polymerization.pdf",
        "data/paper2_composites.pdf",
    ]
    pipeline.build_dataset(pdf_files, output_name="polymer_dataset.jsonl")
    print("Dataset generated at output_dataset/polymer_dataset.jsonl")
