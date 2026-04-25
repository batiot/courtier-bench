import argparse
import os
import sys
try:
    import opendataloader_pdf
except ImportError:
    print("Error: opendataloader-pdf not installed. Run 'pip install opendataloader-pdf'")
    sys.exit(1)

def convert_pdf_to_md(input_path, output_dir):
    """
    Converts PDF file(s) or folder to Markdown using opendataloader-pdf.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    print(f"Converting {input_path} to Markdown...")
    try:
        # Note: convert() supports lists of files or a directory path
        opendataloader_pdf.convert(
            input_path=[input_path] if os.path.isfile(input_path) else input_path,
            output_dir=output_dir,
            format="markdown"
        )
        print(f"Conversion complete. Results saved in {output_dir}")
    except Exception as e:
        print(f"An error occurred during conversion: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown using opendataloader-pdf")
    parser.add_argument("input", help="Path to a PDF file or a directory containing PDFs")
    parser.add_argument("--output", "-o", default="./output", help="Output directory (default: ./output)")
    
    args = parser.parse_args()
    
    # Check if Java is installed (required by the library)
    if os.system("java -version > /dev/null 2>&1") != 0:
        print("Warning: Java 11+ is required but not found in PATH.")
        print("Please install JDK 11+ (e.g., from https://adoptium.net/) to use this tool.")
    
    convert_pdf_to_md(args.input, args.output)
